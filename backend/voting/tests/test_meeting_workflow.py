from datetime import date
from unittest.mock import patch

from backend.account.tests.utils import AuthenticatedTestCase
from backend.voting.models import Ballot, MadeVote, Meeting


class MeetingWorkflowTests(AuthenticatedTestCase):
    def test_attendance_ballot_vote_results_closure_and_next_ballot(self):
        with patch("backend.voting.signals.emit_event"):
            meeting = self.admin_client.post(
                "/voting/admin-meetings/",
                {
                    "name": "Workflow",
                    "clear_data": str(date.today()),
                    "open_attendance": True,
                },
                format="json",
            )
            self.assertEqual(meeting.status_code, 201)
            meeting_id = meeting.data["id"]
            attend = self.member_client.post(
                "/voting/attend/", {"meeting_id": meeting_id}, format="json"
            )
            self.assertEqual(attend.status_code, 201)
            speaker = self.member_client.post(
                "/voting/speakers/", {"meeting_id": meeting_id}, format="json"
            )
            self.assertEqual(speaker.status_code, 201)

            def open_ballot(question):
                response = self.admin_client.post(
                    "/voting/admin-votes/",
                    {
                        "meeting": meeting_id,
                        "question": question,
                        "alternatives": [{"text": "Yes"}, {"text": "No"}],
                    },
                    format="json",
                )
                self.assertEqual(response.status_code, 201)
                return response.data

            ballot = open_ballot("First")
            body = {
                "vote_id": ballot["id"],
                "alternative_id": ballot["alternatives"][0]["id"],
            }
            url = f"/voting/votes/?meeting_id={meeting_id}"
            public = self.member_client.get(url)
            self.assertFalse(public.data[0]["has_voted"])
            self.assertNotIn("num_votes", public.data[0]["alternatives"][0])
            self.assertEqual(
                self.non_member_client.post(
                    "/voting/made_votes/", body, format="json"
                ).status_code,
                403,
            )
            self.assertEqual(
                self.member_client.post(
                    "/voting/made_votes/", body, format="json"
                ).status_code,
                200,
            )
            self.assertTrue(self.member_client.get(url).data[0]["has_voted"])
            self.assertEqual(
                self.member_client.post(
                    "/voting/made_votes/", body, format="json"
                ).status_code,
                403,
            )

            results_url = f"/voting/admin-votes/{ballot['id']}/"
            self.assertEqual(self.member_client.get(results_url).status_code, 403)
            self.assertEqual(
                self.admin_client.get(results_url).data["alternatives"][0]["num_votes"],
                1,
            )
            closed = self.admin_client.patch(
                results_url, {"open": False}, format="json"
            )
            self.assertEqual(closed.status_code, 200)
            self.assertEqual(self.member_client.get(url).data, [])
            self.assertEqual(
                self.member_client.post(
                    "/voting/made_votes/", body, format="json"
                ).status_code,
                403,
            )

            next_ballot = open_ballot("Second")
            self.assertEqual(
                Meeting.objects.get(pk=meeting_id).current_vote_id, next_ballot["id"]
            )
            self.assertFalse(self.member_client.get(url).data[0]["has_voted"])
            self.assertEqual(MadeVote.objects.filter(vote_id=ballot["id"]).count(), 1)
            self.assertEqual(
                Ballot.objects.filter(alternative_id=body["alternative_id"]).count(), 1
            )
            self.assertEqual(
                self.admin_client.get(results_url).data["alternatives"][0]["num_votes"],
                1,
            )

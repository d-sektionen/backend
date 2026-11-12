"""Votes append anonymous Ballot rows; tallies are counted, never stored."""

from datetime import date
from unittest.mock import patch

from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase
from django.test.utils import CaptureQueriesContext

from backend.account.tests.utils import AuthenticatedTestCase
from backend.voting.models import (
    Alternative,
    Attendant,
    Ballot,
    MadeVote,
    Meeting,
    Vote,
)


class BallotTests(AuthenticatedTestCase):
    @classmethod
    def setUpTestData(cls):
        with patch("backend.voting.signals.emit_event"):
            cls.meeting = Meeting.objects.create(
                name="Ballots", clear_data=date.today()
            )
            Attendant.objects.create(user=cls.member, meeting=cls.meeting)
            cls.vote = Vote.objects.create(meeting=cls.meeting, question="Choose")
            cls.yes = Alternative.objects.create(vote=cls.vote, text="Yes")
            cls.no = Alternative.objects.create(vote=cls.vote, text="No")

    def test_ballot_rows_never_reference_a_user(self):
        names = {field.name for field in Ballot._meta.get_fields()}
        self.assertEqual(names, {"id", "alternative"})

    def test_a_vote_appends_one_ballot_and_one_receipt_without_updating_rows(self):
        body = {"vote_id": self.vote.pk, "alternative_id": self.yes.pk}
        with (
            patch("backend.voting.signals.emit_event"),
            CaptureQueriesContext(connection) as queries,
        ):
            response = self.member_client.post(
                "/voting/made_votes/", body, format="json"
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Ballot.objects.filter(alternative=self.yes).count(), 1)
        self.assertEqual(Ballot.objects.filter(alternative=self.no).count(), 0)
        self.assertEqual(
            MadeVote.objects.filter(vote=self.vote, user=self.member).count(), 1
        )
        # No shared row is modified, so concurrent voters never queue on one.
        self.assertFalse(any(q["sql"].startswith("UPDATE") for q in queries))

    def test_results_count_ballots_in_a_bounded_number_of_queries(self):
        Ballot.objects.bulk_create(
            [Ballot(alternative=self.yes) for _ in range(3)]
            + [Ballot(alternative=self.no)]
        )
        url = f"/voting/admin-votes/{self.vote.pk}/"
        self.admin_client.get(url)  # warm the permission cache
        with CaptureQueriesContext(connection) as before:
            response = self.admin_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [(a["text"], a["num_votes"]) for a in response.data["alternatives"]],
            [("Yes", 3), ("No", 1)],
        )
        Alternative.objects.bulk_create(
            [Alternative(vote=self.vote, text=str(i)) for i in range(5)]
        )
        with CaptureQueriesContext(connection) as after:
            response = self.admin_client.get(url)
        self.assertEqual(len(response.data["alternatives"]), 7)
        self.assertEqual(len(after), len(before))

    def test_public_ballot_list_hides_tallies(self):
        Ballot.objects.create(alternative=self.yes)
        response = self.member_client.get(
            f"/voting/votes/?meeting_id={self.meeting.pk}"
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("num_votes", response.data[0]["alternatives"][0])


class BallotMigrationTests(TransactionTestCase):
    old = [("voting", "0014_remove_redundant_receipt_index")]
    new = [("voting", "0015_ballot_rows_replace_counters")]

    def tearDown(self):
        # Leave the schema current so the test runner can flush every table.
        executor = MigrationExecutor(connection)
        executor.migrate(executor.loader.graph.leaf_nodes())

    def test_counters_expand_into_ballots_and_collapse_back(self):
        executor = MigrationExecutor(connection)
        executor.migrate(self.old)
        apps = executor.loader.project_state(self.old).apps
        meeting = apps.get_model("voting", "Meeting").objects.create(
            name="History", clear_data=date.today()
        )
        vote = apps.get_model("voting", "Vote").objects.create(
            meeting=meeting, question="Old"
        )
        Alternative = apps.get_model("voting", "Alternative")
        yes = Alternative.objects.create(vote=vote, text="Yes", num_votes=3)
        no = Alternative.objects.create(vote=vote, text="No", num_votes=0)

        executor = MigrationExecutor(connection)
        executor.migrate(self.new)
        apps = executor.loader.project_state(self.new).apps
        Ballot = apps.get_model("voting", "Ballot")
        self.assertEqual(Ballot.objects.filter(alternative_id=yes.pk).count(), 3)
        self.assertEqual(Ballot.objects.filter(alternative_id=no.pk).count(), 0)
        with connection.cursor() as cursor:
            columns = connection.introspection.get_table_description(
                cursor, "voting_alternative"
            )
        self.assertNotIn("num_votes", {column.name for column in columns})

        executor = MigrationExecutor(connection)
        executor.migrate(self.old)
        Alternative = executor.loader.project_state(self.old).apps.get_model(
            "voting", "Alternative"
        )
        self.assertEqual(Alternative.objects.get(pk=yes.pk).num_votes, 3)
        self.assertEqual(Alternative.objects.get(pk=no.pk).num_votes, 0)

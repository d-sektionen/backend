from django.contrib.auth.models import Group, User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.response import Response
from rest_framework import status

from membership.utils import check_membership
from checkin.models import EventBase


class Meeting(EventBase):
    ACTIONS = ["Lägg till deltagare", "Ta bort deltagare"]

    current_vote = models.ForeignKey(
        "Vote", blank=True, null=True, related_name="+", on_delete=models.CASCADE
    )
    open_attendance = models.BooleanField(
        default=False, help_text="Allows users to set their own attendance."
    )
    enable_speaker_requests = models.BooleanField(default=True)

    @staticmethod
    def get_model_name():
        return "Möte"

    def __str__(self):
        return self.name

    def on_register(self, user, action):
        if action == "0":
            if not check_membership(user.username):
                return Response(
                    {
                        "detail": "User is not a member of D-sektionen.",
                        "status_message": self.get_status_message(),
                    },
                    status.HTTP_400_BAD_REQUEST,
                )

            attendant, created = Attendant.objects.get_or_create(
                user=user, meeting=self
            )
            if not created:
                return Response(
                    {
                        "detail": user.username
                        + " is already registered on the meeting.",
                        "status_message": self.get_status_message(),
                    },
                    status.HTTP_400_BAD_REQUEST,
                )
            return Response(
                {
                    "detail": user.username + " was successfully registered.",
                    "icon": "FiUserCheck",
                    "status_message": self.get_status_message(),
                },
                status.HTTP_200_OK,
            )

        elif action == "1":
            attendant = Attendant.objects.filter(user=user, meeting=self).first()
            if attendant is not None:
                attendant.delete()
                return Response(
                    {
                        "detail": user.username + " was successfully unregistered.",
                        "icon": "FiUserX",
                        "status_message": self.get_status_message(),
                    },
                    status.HTTP_200_OK,
                )
            return Response(
                {
                    "detail": user.username + " is not registered on the meeting.",
                    "status_message": self.get_status_message(),
                },
                status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"detail": "Unknown action", "status_message": self.get_status_message()},
            status.HTTP_400_BAD_REQUEST,
        )

    def get_status_message(self):
        attendee_count = Attendant.objects.filter(meeting__id=self.id).count()
        count_str = f"{attendee_count}"
        status_str = f"Meeting currently has {count_str} registered attendees."
        return status_str


class Attendant(models.Model):
    user = models.ForeignKey(User, null=False, on_delete=models.CASCADE)
    meeting = models.ForeignKey(
        Meeting, null=False, related_name="attendants", on_delete=models.CASCADE
    )

    @staticmethod
    def get_model_name():
        return "Deltagare"

    class Meta:
        unique_together = ("user", "meeting")


class Vote(models.Model):
    question = models.CharField(max_length=128)
    open = models.BooleanField(default=True)
    meeting = models.ForeignKey(Meeting, null=False, on_delete=models.CASCADE)

    @staticmethod
    def get_model_name():
        return "Röst"

    def __str__(self):
        return self.question


@receiver(post_save, sender=Vote)
def update_current_vote(sender, instance, created, **kwargs):
    """
    Closes the old meeting vote and sets the meeting's current vote to the new one.
    """

    if instance.open:
        meeting = instance.meeting
        old_vote = meeting.current_vote
        if old_vote is not None and old_vote != instance:
            old_vote.open = False
            old_vote.save()

        meeting.current_vote = instance
        meeting.save()


class Alternative(models.Model):
    text = models.CharField(max_length=64)
    num_votes = models.IntegerField(default=0)
    vote = models.ForeignKey(Vote, null=False, on_delete=models.CASCADE)

    @staticmethod
    def get_model_name():
        return "Alternativ"


class MadeVote(models.Model):
    user = models.ForeignKey(User, null=False, on_delete=models.CASCADE)
    vote = models.ForeignKey(Vote, null=False, on_delete=models.CASCADE)


class SpeakerRequest(models.Model):
    user = models.ForeignKey(User, null=False, on_delete=models.CASCADE)
    meeting = models.ForeignKey(Meeting, null=False, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("user", "meeting")

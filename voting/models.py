from django.contrib.auth.models import Group, User
from django.db import models

from account.models import Section


class Meeting(models.Model):
    name = models.CharField(max_length=64)
    current_vote = models.ForeignKey('Vote', blank=True, null=True, related_name='+')
    section = models.ForeignKey(Section, null=False)
    archived = models.BooleanField(default=False)

    class Meta:
        permissions = (
            ("create_meeting", "Can create Meeting"),
            ("read_meeting", "Can read Meeting"),
            ("update_meeting", "Can update Meeting"),
            ("delete_meeting", "Can delete Meeting"),
            ("list_meetings", "Can list Meetings")
        )

    def __str__(self):
        return self.name


class Scanner(models.Model):
    user = models.ForeignKey(User, null=False)
    meeting = models.ForeignKey(Meeting, null=False)

    class Meta:
        unique_together = ('user', 'meeting')
        permissions = (
            ("create_scanner", "Can create Scanner"),
            ("delete_scanner", "Can delete Scanner"),
            ("list_scanners", "Can list Scanners")
        )


class Attendant(models.Model):
    user = models.ForeignKey(User, null=False)
    meeting = models.ForeignKey(Meeting, null=False)

    class Meta:
        unique_together = ('user', 'meeting')
        permissions = (
            ("create_attendant", "Can create Attendant"),
            ("delete_attendant", "Can delete Attendant"),
            ("list_attendants", "Can list Attendants")
        )


class Vote(models.Model):
    question = models.CharField(max_length=128)
    open = models.BooleanField(default=True)
    meeting = models.ForeignKey(Meeting, null=False)

    class Meta:
        permissions = (
            ("create_vote", "Can create Vote"),
            ("read_vote", "Can read Vote"),
            ("update_vote", "Can update Vote"),
            ("delete_vote", "Can delete Vote"),
            ("list_votes", "Can list Votes")
        )

    def __str__(self):
        return self.question


class Alternative(models.Model):
    text = models.CharField(max_length=64)
    num_votes = models.IntegerField(default=0)
    vote = models.ForeignKey(Vote, null=False)

    class Meta:
        permissions = ()


class MadeVote(models.Model):
    user = models.ForeignKey(User, null=False)
    vote = models.ForeignKey(Vote, null=False)

    class Meta:
        permissions = (
            ("create_made_vote", "Can create MadeVote")
        )

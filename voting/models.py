from django.contrib.auth.models import Group, User
from django.db import models

from account.models import Section


class Meeting(models.Model):
    name = models.CharField(max_length=64)
    current_vote = models.ForeignKey('Vote', blank=True, null=True, related_name='+')
    section = models.ForeignKey(Section, null=False)
    archived = models.BooleanField(default=False)

    @staticmethod
    def get_model_name():
        return "Möte"

    def __str__(self):
        return self.name


class Scanner(models.Model):
    user = models.ForeignKey(User, null=False)
    meeting = models.ForeignKey(Meeting, null=False)

    @staticmethod
    def get_model_name():
        return "Skannare"

    class Meta:
        unique_together = ('user', 'meeting')


class Attendant(models.Model):
    user = models.ForeignKey(User, null=False)
    meeting = models.ForeignKey(Meeting, null=False)

    @staticmethod
    def get_model_name():
        return "Deltagare"

    class Meta:
        unique_together = ('user', 'meeting')


class Vote(models.Model):
    question = models.CharField(max_length=128)
    open = models.BooleanField(default=True)
    meeting = models.ForeignKey(Meeting, null=False)

    @staticmethod
    def get_model_name():
        return "Röst"

    def __str__(self):
        return self.question


class Alternative(models.Model):
    text = models.CharField(max_length=64)
    num_votes = models.IntegerField(default=0)
    vote = models.ForeignKey(Vote, null=False)

    @staticmethod
    def get_model_name():
        return "Alternativ"


class MadeVote(models.Model):
    user = models.ForeignKey(User, null=False)
    vote = models.ForeignKey(Vote, null=False)


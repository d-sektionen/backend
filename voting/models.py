import re

from django.contrib.auth.models import Group, User
from django.db import models


class Section(models.Model):
    name = models.TextField()
    program_codes = models.TextField()
    user_group = models.ForeignKey(Group, blank=True, null=True, related_name='+')
    admin_group = models.ForeignKey(Group, blank=True, null=True, related_name='+')

    def get_program_codes(self):
        items = re.split('[, \n]', self.program_codes)  # Split
        items = [x.strip() for x in items]              # Strip
        items = [x for x in items if x]                 # Filter

        return items

    def get_user_group(self):
        if not self.user_group:
            self.user_group = Group.objects.create(name=self.name)
            self.save(update_fields=['user_group'])

        return self.user_group

    def get_admin_group(self):
        if not self.admin_group:
            self.admin_group = Group.objects.create(name='Admin for ' + self.name)
            self.save(update_fields=['admin_group'])

        return self.admin_group


class Meeting(models.Model):
    name = models.CharField(max_length=64)
    current_vote = models.ForeignKey('Vote', blank=True, null=True, related_name='+')
    section = models.ForeignKey(Section, null=False)
    archived = models.BooleanField(default=False)


class Scanner(models.Model):
    user = models.ForeignKey(User, null=False)
    meeting = models.ForeignKey(Meeting, null=False)


class Attendant(models.Model):
    user = models.ForeignKey(User, null=False)
    meeting = models.ForeignKey(Meeting, null=False)


class Vote(models.Model):
    question = models.CharField(max_length=128)
    open = models.BooleanField(default=True)
    meeting = models.ForeignKey(Meeting, null=False)


class Alternative(models.Model):
    text = models.CharField(max_length=64)
    num_votes = models.IntegerField(default=0)
    vote = models.ForeignKey(Vote, null=False)


class MadeVote(models.Model):
    user = models.ForeignKey(User, null=False)
    vote = models.ForeignKey(Vote, null=False)

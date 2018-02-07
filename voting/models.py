import re

from django.contrib.auth.models import Group, User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


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

    def __str__(self):
        return self.name


@receiver(post_save, sender=Section)
def create_section_groups(sender, instance, created, **kwargs):
    if created:
        # Create user and admin groups
        instance.user_group = Group.objects.create(name=instance.name)
        instance.admin_group = Group.objects.create(name='Admins for ' + instance.name)
        instance.save(update_fields=['user_group', 'admin_group'])


class Meeting(models.Model):
    name = models.CharField(max_length=64)
    current_vote = models.ForeignKey('Vote', blank=True, null=True, related_name='+')
    section = models.ForeignKey(Section, null=False)
    archived = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Scanner(models.Model):
    user = models.ForeignKey(User, null=False)
    meeting = models.ForeignKey(Meeting, null=False)

    class Meta:
        unique_together = ('user', 'meeting')


class Attendant(models.Model):
    user = models.ForeignKey(User, null=False)
    meeting = models.ForeignKey(Meeting, null=False)

    class Meta:
        unique_together = ('user', 'meeting')


class Vote(models.Model):
    question = models.CharField(max_length=128)
    open = models.BooleanField(default=True)
    meeting = models.ForeignKey(Meeting, null=False)

    def __str__(self):
        return self.question


class Alternative(models.Model):
    text = models.CharField(max_length=64)
    num_votes = models.IntegerField(default=0)
    vote = models.ForeignKey(Vote, null=False)


class MadeVote(models.Model):
    user = models.ForeignKey(User, null=False)
    vote = models.ForeignKey(Vote, null=False)

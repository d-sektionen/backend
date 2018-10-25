import re

from django.contrib.auth.models import Group, User
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


def is_user_in_group(group, user):
    if group is None or user is None:
        return False

    return group in user.groups.all()

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    liu_card_id = models.CharField(max_length=30, blank=True)

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

@receiver(post_delete, sender=Profile)
def post_delete_user(sender, instance, *args, **kwargs):
    if instance.user:
        instance.user.delete()

class Section(models.Model):
    name = models.TextField()
    program_codes = models.TextField()
    user_group = models.ForeignKey(Group, blank=True, null=True, related_name='section_user_group')
    admin_group = models.ForeignKey(Group, blank=True, null=True, related_name='section_admin_group')

    def get_program_codes(self):
        items = re.split('[, \n]', self.program_codes)  # Split
        items = [x.strip() for x in items]  # Strip
        items = [x for x in items if x]  # Filter

        return items

    def is_member(self, user):
        return is_user_in_group(self.user_group, user)

    def is_admin(self, user):
        return is_user_in_group(self.admin_group, user)

    def __str__(self):
        return self.name


@receiver(post_save, sender=Section)
def create_section_groups(sender, instance, created, **kwargs):
    if created:
        # Create user and admin groups
        instance.user_group = Group.objects.create(name=instance.name)
        instance.admin_group = Group.objects.create(name='Admins for ' + instance.name)
        instance.save(update_fields=['user_group', 'admin_group'])

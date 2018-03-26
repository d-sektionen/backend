import re

from django.contrib.auth.models import Group
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


def is_user_in_group(group, user):
    if user is None:
        return False

    return group in user.groups.all()


class Section(models.Model):
    name = models.TextField()
    program_codes = models.TextField()
    user_group = models.ForeignKey(Group, blank=True, null=True, related_name='+')
    admin_group = models.ForeignKey(Group, blank=True, null=True, related_name='+')

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

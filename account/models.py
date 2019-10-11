from django.contrib.auth.models import Group, User
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

# Can be moved if you cba.
def is_user_in_group(group, user):
    if group is None or user is None:
        return False

    return group in user.groups.all()


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    liu_card_id = models.BigIntegerField(null=True, blank=True, default=None)
    infomail_subscriber = models.BooleanField(default=False)

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

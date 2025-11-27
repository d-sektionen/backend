import uuid
from datetime import datetime
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from ..booking.models import ItemPool
from ..committee.models import CommitteeMember


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    liu_card_id = models.CharField(max_length=17, null=True, blank=True, default=None)
    infomail_subscriber = models.BooleanField(default=True)

    def __str__(self):
        return self.user.username

    def has_active_committee_membership(self):
        return CommitteeMember.objects.filter(
            profile_id=self.id, has_permissions_until__gte=datetime.now()
        ).exists()


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


class CalendarSubscription(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    include_bookings_by_user = models.BooleanField(default=True)
    include_bookable_items = models.ManyToManyField(ItemPool, default=None, blank=True)

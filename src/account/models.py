from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
import uuid
from booking.models import Item



class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    liu_card_id = models.CharField(max_length=17, null=True, blank=True, default=None)
    infomail_subscriber = models.BooleanField(default=True)

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


class CalendarSubscription(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    include_bookings_by_user = models.BooleanField(default=True)
    include_bookable_items = models.ManyToManyField(Item)

class EmailSubscription(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    include_infomail = models.BooleanField(default=True)
    include_announcement = models.BooleanField(default=True)
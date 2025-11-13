from django.db import models
from django.core.validators import URLValidator
from django.contrib.auth.models import User
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from .validators import validate_datetime_future, validate_datetime_within_year


class Blacklisted(models.Model):
    user = models.OneToOneField(User, null=False, on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)
    expires = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.user


WEBHOOK_SERVICES_CHOICES = [("discord", "Discord"), ("slack", "Slack")]


class Webhook(models.Model):
    name = models.CharField(max_length=32, unique=True)
    service = models.CharField(
        max_length=7, choices=WEBHOOK_SERVICES_CHOICES, default="slack"
    )
    url = models.CharField(
        max_length=2048,
        default=None,
        null=True,
        unique=True,
        validators=[URLValidator()],
    )

    def __str__(self):
        return self.name


class ItemCategory(models.Model):
    name = models.CharField(max_length=32, unique=True)

    def __str__(self):
        return self.name


class Item(models.Model):
    name = models.CharField(max_length=32, unique=True)
    description = models.TextField(max_length=512)
    category = models.ForeignKey(
        ItemCategory, null=True, blank=True, on_delete=models.SET_NULL
    )
    terms = models.FileField(null=True, blank=True, upload_to="booking_terms")
    image = models.ImageField(null=True, blank=True, upload_to="booking_images")
    image_processed = ImageSpecField(
        source="image",
        processors=[ResizeToFill(960, 400)],
        format="JPEG",
        options={"quality": 80},
    )
    requires_confirmation = models.BooleanField(default=False)
    enabled = models.BooleanField(default=True)
    webhook = models.ForeignKey(
        Webhook, null=True, blank=True, on_delete=models.SET_NULL
    )

    def __str__(self):
        return self.name


class Booking(models.Model):
    start = models.DateTimeField(validators=[validate_datetime_future])
    end = models.DateTimeField(validators=[validate_datetime_within_year])
    user = models.ForeignKey(User, null=False, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, null=False, on_delete=models.CASCADE)
    description = models.TextField()
    confirmed = models.BooleanField(default=False)
    restricted_timeslot = models.BooleanField(default=False, blank=True)

    def __str__(self):
        return self.user.username + " - " + self.description[:32]

    # def clean(self):
    #   # Start should be before end
    #   if self.start > self.end:
    #     raise ValidationError('Booking should start before it ends.')
    #   # Check lowest duration
    #   if self.start + timedelta(minutes=30) > self.end:
    #     raise ValidationError('Booking should be at least 30 minutes.')
    #   # Check longest duration
    #   if self.start + timedelta(days=7) < self.end:
    #     raise ValidationError('Booking should be at most 7 days.')

    #   # Check overlap
    #   if Booking.objects\
    #     .filter(item=self.item)\
    #     .exclude(id=self.id)\
    #     .filter(start__lte=self.end, end__gte=self.start)\
    #     .exists():
    #     raise ValidationError('Booking overlaps with another booking.')

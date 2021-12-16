from django.db import models
from django.contrib.auth.models import User
from django.db.models.fields import FloatField
from .validators import validate_datetime_future, validate_datetime_within_year
from django.core.exceptions import ValidationError
from datetime import timedelta
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill

class Article(models.Model):
    specification = models.TextField(max_length=512, blank=False)
    amount = models.IntegerField(blank=False)
    price = models.FloatField(blank=False)
    total = models.FloatField(blank=False)
    #terms = models.FileField(null=True, blank=True, upload_to="booking_terms")
    #image = models.ImageField(null=True, blank=True, upload_to="booking_images")
    """image_processed = ImageSpecField(
        source="image",
        processors=[ResizeToFill(960, 400)],
        format="JPEG",
        options={"quality": 80},
    )"""

    def __str__(self):
        return self.name



class BudgetEntry(models.Model):
    date = models.DateTimeField(validators=[validate_datetime_future])
    user = models.ForeignKey(User, null=False, on_delete=models.CASCADE)
    name = models.TextField(blank=False)
    location = models.TextField(blank=False)
    #articles = models.ManyToManyField(Article,  blank=True)
    articles = models.TextField(blank=True)
    description = models.TextField(blank=False)
    clearingNr = models.TextField()
    bankNr = models.TextField()
    bankName = models.TextField()
    committee = models.TextField()
    confirmed = models.BooleanField(default=False)
    approvedKas = models.BooleanField(default=False, blank=True)
    approvedDeg = models.BooleanField(default=False, blank=True)
    payed = models.BooleanField(default=False, blank=True)
    ipaddr = models.GenericIPAddressField()
    image = models.ImageField(null=True, blank=True, upload_to="exspense_receipt")
    image_processed = ImageSpecField(
        source="image",
        #processors=[ResizeToFill(960, 400)],
        format="JPEG",
        options={"quality": 80},
    )
    
    total_sum = FloatField(default=0, blank=False)


    def __str__(self):
        return self.user.username + " - " + self.description[:32]

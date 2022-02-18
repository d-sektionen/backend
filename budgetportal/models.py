from django.db import models
from django.contrib.auth.models import User
from django.db.models.fields import FloatField
from .validators import validate_datetime_future, validate_datetime_within_year
from django.core.exceptions import ValidationError
from datetime import timedelta
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from committee.models import Committee

class BudgetEntry(models.Model):
    date = models.DateTimeField()
    user = models.ForeignKey(User, null=False, on_delete=models.CASCADE)
    name = models.TextField(blank=False)
    location = models.TextField(blank=False)
    articles = models.TextField(blank=True)
    description = models.TextField(blank=False)
    clearingNr = models.TextField()
    bankNr = models.TextField()
    bankName = models.TextField()
    committee = models.ForeignKey(Committee, null=False, on_delete=models.CASCADE)
    confirmed = models.BooleanField(default=False)
    approvedKas = models.BooleanField(default=False, blank=True)
    approvedDeg = models.BooleanField(default=False, blank=True)
    payed = models.BooleanField(default=False, blank=True)
    ipaddr = models.GenericIPAddressField()
    comment = models.TextField(default="",blank=True, null=True)
    total_sum = FloatField(default=0, blank=False)
    report_pdf = models.FileField(upload_to='documents/%Y/%m/%d/',null=True, blank=True)

    def __str__(self):
        return self.user.username + " - " + self.description[:32]


class File(models.Model):
    file = models.FileField(null=True, blank=True, upload_to="expense_receipt/%Y/%m/%d/")
    expense = models.ForeignKey(BudgetEntry, on_delete=models.CASCADE, null=True)
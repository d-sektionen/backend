import json
from django.contrib.auth.models import User
from django.db import models


from ..committee.models import Committee


class BudgetEntry(models.Model):
    articles = models.TextField(blank=True)
    description = models.TextField(blank=False)

    clearingNr = models.TextField()
    bankNr = models.TextField()
    bankName = models.TextField()

    committee = models.ForeignKey(Committee, null=False, on_delete=models.CASCADE)
    name = models.TextField(blank=False)
    user = models.ForeignKey(User, null=False, on_delete=models.CASCADE)
    location = models.TextField(blank=False)
    date = models.DateTimeField()
    ipaddr = models.GenericIPAddressField()
    report_pdf = models.FileField(
        upload_to="documents/%Y/%m/%d/", null=True, blank=True
    )

    confirmed = models.BooleanField(default=False)  # type: ignore[type]
    approvedKas = models.BooleanField(default=False, blank=True)  # type: ignore[type]
    approvedDeg = models.BooleanField(default=False, blank=True)  # type: ignore[type]
    payed = models.BooleanField(default=False, blank=True)  # type: ignore[type]
    denied = models.BooleanField(default=False, blank=True)  # type: ignore[type]
    comment = models.TextField(default="", blank=True, null=True)

    class Meta:
        ordering = ("date",)

    @property
    def total_sum(self):
        sum = 0.0

        # Convert articles json string to json object
        articles = json.loads(str(self.articles).replace("'", '"'))
        for article in articles:
            sum += article["amount"] * article["price"]

        return sum

    def __str__(self):
        return self.user.username + " - " + self.description[:32]  # type: ignore[attr-defined]


class File(models.Model):
    file = models.FileField(
        null=True, blank=True, upload_to="expense_receipt/%Y/%m/%d/"
    )
    expense = models.ForeignKey(
        BudgetEntry, related_name="receipts", on_delete=models.CASCADE, null=True
    )

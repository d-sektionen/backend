from django.db import models
from post_office.models import Email
from django.contrib.auth.models import User

CATEGORIES = (
    ("infomail", "INFOMAIL"),
    ("announcement", "ANNOUNCEMENT"),
    ("uncategorized", "UNCATEGORIZED"),
)


class Mail(models.Model):
    category = models.CharField(
        max_length=50,
        choices=CATEGORIES,
        default="uncategorized",
    )

    subject = models.CharField(max_length=255)
    html = models.TextField()
    post_office_mail = models.ForeignKey(Email, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, null=False, on_delete=models.CASCADE)

    def __str__(self):
        return self.subject


class MailTemplate(models.Model):
    name = models.CharField(max_length=255)
    category = models.CharField(
        max_length=50,
        choices=CATEGORIES,
        default="uncategorized",
    )
    subject = models.CharField(max_length=255)
    description = models.TextField(max_length=500)
    # TODO: Different field type?
    template_filename = models.CharField(max_length=100)

    def __str__(self):
        return self.name

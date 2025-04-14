from django.db import models


class Email(models.Model):
    category = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    html = models.TextField()
    sendAt = models.DateTimeField()

    def __str__(self):
        return self.subject


class EmailTemplate(models.Model):
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    description = models.TextField(max_length=500)
    template_file = models.FileField(upload_to="templates/email")

    def __str__(self):
        return self.name

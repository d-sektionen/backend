from django.db import models


class Section(models.Model):
    name = models.TextField()
    program_codes = models.TextField()

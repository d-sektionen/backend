from django.db import models
from django.contrib.auth.models import Permission

from account.models import Profile


ROLE_TYPES = (
    ("tr", "treasurer"),
    ("ch", "chair"),
    ("ot", "other"),
)


class Committee(models.Model):
    name = models.CharField(max_length=64)
    description = models.CharField(max_length=255, blank=True)
    chairman_permissions = models.ManyToManyField(
        Permission, related_name="chairman_permissions"
    )
    treasurer_permissions = models.ManyToManyField(
        Permission, related_name="treasurer_permissions"
    )
    other_permissions = models.ManyToManyField(
        Permission, related_name="other_permissions"
    )

    def __str__(self):
        return self.name


class CommitteeMember(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    email = models.EmailField(null=True)
    role_name = models.CharField(max_length=255)
    role_type = models.CharField(
        max_length=2,
        choices=ROLE_TYPES,
        default="ot",
    )
    year = models.CharField(max_length=5)
    committee = models.ForeignKey(Committee, on_delete=models.CASCADE)
    has_permissions_until = models.DateField()

    def __str__(self):
        return f"{self.profile.user.username} - {self.committee.name} - {self.year}"

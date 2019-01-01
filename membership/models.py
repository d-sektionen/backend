from django.db import models


"""
Model for a section member in D-sektionen.
"""
class Member(models.Model):
    MEMBERSHIP_TYPE_CHOICES = (
        ('S', 'Student Member'),
        ('A', 'Alumni Member'),
        ('H', 'Honorary Member'),
        ('O', 'Other'),
    )
    liu_id = models.CharField(max_length=8, unique=True)
    first_name = models.CharField(max_length=64, blank=True)
    last_name = models.CharField(max_length=64, blank=True)
    membership_type = models.CharField(
        max_length=2,
        choices=MEMBERSHIP_TYPE_CHOICES,
        default='S',
    )

    def __str__(self):
        return self.liu_id

"""
Stores a program registration of a member to track if they still study.
Not currently in use but may be useful in the future.
Try to keep up to date if possible.
"""
class ProgramRegistration(models.Model):
    member = models.ForeignKey('Member', on_delete=models.CASCADE)
    registration = models.CharField(max_length=15) # For example 6cite-10-ht2018

    def __str__(self):
        return self.registration + ' - ' + self.member.liu_id
from django.db import models


class Member(models.Model):
    """
    Model for a section member in D-sektionen.
    """

    MEMBERSHIP_TYPE_CHOICES = (
        ("S", "Student Member"),
        ("A", "Alumni Member"),
        ("H", "Honorary Member"),
        ("O", "Other"),
    )
    liu_id = models.CharField(max_length=8, unique=True)
    first_name = models.CharField(max_length=64, blank=True)
    last_name = models.CharField(max_length=64, blank=True)
    membership_type = models.CharField(
        max_length=2, choices=MEMBERSHIP_TYPE_CHOICES, default="S"
    )

    def __str__(self):
        return self.liu_id


class ProgramRegistration(models.Model):
    """
    Stores a program registration of a member to track if they still study.
    Not currently in use but may be useful in the future.
    Try to keep up to date if possible.
    """

    member = models.ForeignKey("Member", on_delete=models.CASCADE)
    registration = models.CharField(max_length=15)  # For example 6cite-10-ht2018

    def __str__(self):
        return f"{self.registration} - {self.member.liu_id}"


class Request(models.Model):
    """
    Model for requesting to become a section Member.
    """

    PROGRAM_CHOICES = (
        ("D", "Datateknik"),
        ("U", "Mjukvaruteknik"),
        ("IT", "Informationsteknologi"),
        ("IP", "Innovativ Programering"),
        ("CS", "Computer Science"),
        ("CY", "Cyber Security"),
    )

    username = models.CharField(max_length=200, unique=True)
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    message = models.CharField(max_length=256, blank=True)
    program = models.CharField(max_length=2, choices=PROGRAM_CHOICES, blank=True)
    starting_year = models.IntegerField()
    timestamp = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.username}, {self.program}"

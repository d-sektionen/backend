from django.db import models
from django.contrib.auth.models import User

from committee.models import Committee
from booking.models import Booking

CAR_DAILY_COST = 30
TRAILER_DAILY_COST = 100
COST_PER_KM = 3  # For section members


class LogStart(models.Model):
    logging_user = models.ForeignKey(
        User, null=True, on_delete=models.SET_NULL, related_name='carlogging_starts_logging_user')
    booking_user = models.ForeignKey(
        User, null=True, on_delete=models.SET_NULL, related_name='carlogging_starts_booking_user')
    car_booking = models.OneToOneField(
        Booking, null=True, on_delete=models.SET_NULL, related_name='carlogging_starts_car_booking')
    kilometers = models.IntegerField(null=False)
    message = models.TextField(blank=True, max_length=200)
    car_cleaned = models.BooleanField(null=False)
    logging_date = models.DateTimeField(auto_now_add=True)


class LogEntry(models.Model):
    logging_user = models.ForeignKey(
        User, null=True, on_delete=models.SET_NULL, related_name='carlogging_entries_logging_user')
    booking_user = models.ForeignKey(
        User, null=True, on_delete=models.SET_NULL, related_name='carlogging_entries_booking_user')
    log_start = models.OneToOneField(
        LogStart, null=True, on_delete=models.CASCADE, related_name='log_entry')
    committee = models.ForeignKey(
        Committee, null=True, on_delete=models.SET_NULL)
    kilometers = models.IntegerField(null=False)
    message = models.TextField(blank=True, max_length=200)
    car_cleaned = models.BooleanField(null=False)
    logging_date = models.DateTimeField(auto_now_add=True)
    
    car_days = models.IntegerField(null=False, default=1)
    trailer_user = models.ForeignKey(
        User, null=True, on_delete=models.SET_NULL, related_name='carlogging_entries_trailer_user')
    trailer_booking = models.OneToOneField(
        Booking, null=True, on_delete=models.SET_NULL, related_name='carlogging_entries_trailer_booking')
    trailer_days = models.IntegerField(null=False, default=1)
    cost = models.IntegerField(null=True)
    paid = models.BooleanField(default=False)  # Should be marked by the payment reciever as paid

    def calc_cost(self):
        if self.logging_user is None:
            return 0

        km_cost = (self.kilometers - self.log_start.kilometers) * COST_PER_KM
        car_cost = (self.car_days - 1) * CAR_DAILY_COST
        trailer_cost = self.trailer_days * TRAILER_DAILY_COST

        return km_cost + car_cost + trailer_cost

    def save(self, *args, **kwargs):
        if not self.id:
            # This is a new object
            return super(LogEntry, self).save(*args, **kwargs)
        else:
            # An existing object has been edited
            super(LogEntry, self).save(*args, **kwargs)
            self.cost = self.calc_cost()
            super(LogEntry, self).save(*args, **kwargs)

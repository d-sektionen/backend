from django.db import models
from django.contrib.auth.models import User
from membership.utils import check_membership

DAILY_COST = 30
TRAILER_DAILY_COST = 100


class LogStart(models.Model):
    logging_user = models.ForeignKey(
        User, null=True, on_delete=models.SET_NULL, related_name="carlogging_starts_logging"
    )
    booking_user = models.ForeignKey(
        User, null=True, on_delete=models.SET_NULL, related_name="carlogging_starts_booking"
    )
    start_km = models.IntegerField(null=False)
    start_message = models.TextField(blank=False, max_length=200)
    start_car_cleaned = models.BooleanField(null=False)
    logging_finished = models.BooleanField(null=True)
    logging_date = models.DateTimeField(auto_now_add=True)


class LogEntry(models.Model):
    logging_user = models.ForeignKey(
        User, null=True, on_delete=models.SET_NULL, related_name="carlogging_entries_logging"
    )
    booking_user = models.ForeignKey(
        User, null=True, on_delete=models.SET_NULL, related_name="carlogging_entries_booking"
    )
    log_start = models.ForeignKey(
        LogStart, null=True, on_delete=models.CASCADE)
    car_days = models.IntegerField(null=True)
    cost = models.IntegerField(null=True)
    trailer = models.BooleanField(default=False)
    trailer_days = models.IntegerField(null=True)
    active_member = models.BooleanField(default=False)  # sektionsaktiv
    member = models.BooleanField(default=False)  # sektionsmedlem

    # should be marked by the payment reciever as paid:
    paid = models.BooleanField(default=False)
    end_message = models.TextField(blank=True, max_length=200, null=False)
    end_km = models.IntegerField(null=False)
    end_car_cleaned = models.BooleanField(null=False)

    logging_date = models.DateTimeField(auto_now_add=True)

    def calc_cost(self):
        if self.logging_user is None:
            return 0
        # TODO: move magic numbers
        # Daily cost of trailer

        # Cost of per kilometer travelled using the car, depending on user.
        cost_per_km = (
            3 if self.active_member
            else (4 if check_membership(self.logging_user.username) else 6)
        )

        # if user only used the trailer
        if self.log_start.start_km is None or self.end_km is None:
            if not self.trailer:
                return 0
            return TRAILER_DAILY_COST * self.trailer_days

        # calculate cost of the car usage
        cost = 0
        if self.trailer:
            cost += TRAILER_DAILY_COST * self.trailer_days

        km_travelled = self.end_km - self.log_start.start_km
        km_cost_sum = km_travelled * cost_per_km

        daily_cost_sum = (self.car_days - 1) * DAILY_COST

        cost += km_cost_sum + daily_cost_sum
        return cost

    def save(self, *args, **kwargs):
        if not self.id:
            # this is a new object:
            return super(LogEntry, self).save(*args, **kwargs)
        else:
            # an existing object has been edited:
            super(LogEntry, self).save(*args, **kwargs)
            self.cost = self.calc_cost()
            super(LogEntry, self).save(*args, **kwargs)

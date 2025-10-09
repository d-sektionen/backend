from django.db import models
from django.contrib.auth.models import User
from ..membership.utils import check_membership


class LogEntry(models.Model):
    start_km = models.IntegerField(null=True)
    end_km = models.IntegerField(null=True)
    car_days = models.IntegerField(null=True)
    user = models.ForeignKey(
        User, null=True, on_delete=models.SET_NULL, related_name="carlogging_entries"
    )
    cost = models.IntegerField(null=True)
    trailer = models.BooleanField(default=False)
    trailer_days = models.IntegerField(null=True)
    active_member = models.BooleanField(default=False)
    # should be marked by the payment reciever as paid.
    paid = models.BooleanField(default=False)

    def calc_cost(self):
        if self.user is None:
            return 0
        # TODO: move magic numbers
        # Daily cost of trailer
        trailer_daily_cost = 100

        # Cost of per kilometer travelled using the car, depending on user.
        cost_per_km = (
            3
            if self.active_member
            else (4 if check_membership(self.user.username) else 6)
        )
        # starting cost of using the car
        start_cost = (
            0 if self.active_member or self.car_days == 1 or self.car_days == 0 else 30
        )

        # if user only used the trailer
        if self.start_km is None or self.end_km is None:
            if not self.trailer:
                return 0
            return trailer_daily_cost * self.trailer_days

        # calculate cost of the car usage
        cost = 0
        if self.trailer:
            cost += trailer_daily_cost * self.trailer_days
        cost += (self.end_km - self.start_km) * cost_per_km + (
            self.car_days - 1
        ) * start_cost
        return cost

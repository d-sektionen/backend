from django.contrib import admin
from .models import LogEntry


class LogEntryAdmin(admin.ModelAdmin):
    model = LogEntry
    list_display = (
        "end_km",
        "logging_user",
        "calc_cost",
        "trailer",
        "trailer_days",
        "car_days",
        "active_member",
    )
    list_filter = ("logging_user",)
    search_fields = ("user__username", "user__first_name", "user__last_name")


# TODO: add LogStartAdmin

admin.site.register(LogEntry, LogEntryAdmin)

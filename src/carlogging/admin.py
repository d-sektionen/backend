from django.contrib import admin
from .models import LogEntry


class LogEntryAdmin(admin.ModelAdmin):
    model = LogEntry
    list_display = (
        "start_km",
        "end_km",
        "user",
        "calc_cost",
        "trailer",
        "trailer_days",
        "car_days",
        "active_member",
    )
    list_filter = ("user",)
    search_fields = ("user__username", "user__first_name", "user__last_name")


admin.site.register(LogEntry, LogEntryAdmin)

from django.contrib import admin
from .models import Logg


class LogginAdmin(admin.ModelAdmin):
    model = Logg
    list_display = ("start_km", "end_km", "user", "cost", "trailer", "trailer_days", "car_days", "active_member")
    list_filter = ("user",)
    search_fields = (
        "user__username",
        "user__first_name",
        "user__last_name",
    )

admin.site.register(Logg, LogginAdmin)
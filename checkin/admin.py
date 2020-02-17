from django.contrib import admin

from .models import EventBase, Doorkeeper


class EventBaseAdmin(admin.ModelAdmin):
    list_display = ("name", "archived")
    list_filter = ("archived",)
    search_fields = ("name",)


class DoorkeeperAdmin(admin.ModelAdmin):
    list_display = ("user", "event")
    list_filter = ("event",)
    search_fields = (
        "user__username",
        "user__first_name",
        "user__last_name",
        "event__name",
    )


admin.site.register(EventBase, EventBaseAdmin)
admin.site.register(Doorkeeper, DoorkeeperAdmin)

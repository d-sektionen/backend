from django.contrib import admin

from .models import Profile


class ProfileAdmin(admin.ModelAdmin):
    readonly_fields = ("user",)
    list_display = ("user", "liu_card_id", "infomail_subscriber")
    list_filter = ("infomail_subscriber",)
    search_fields = (
        "user__username",
        "user__first_name",
        "user__last_name",
        "liu_card_id",
    )


admin.site.register(Profile, ProfileAdmin)

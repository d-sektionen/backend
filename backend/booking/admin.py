from django.contrib import admin
from .models import (
    ItemPool,
    Booking,
    Blacklisted,
    ItemPoolAccessory,
    ItemCategory,
    ItemPoolItem,
    Webhook,
)


class BookingAdmin(admin.ModelAdmin):
    model = Booking
    list_display = (
        "user",
        "pool",
        "start",
        "end",
        "description",
        "restricted_timeslot",
        "confirmed",
    )
    list_filter = (
        "start",
        "end",
        ("user", admin.RelatedOnlyFieldListFilter),
        "restricted_timeslot",
        "confirmed",
        "pool",
    )
    search_fields = (
        "user__username",
        "user__first_name",
        "user__last_name",
        "description",
    )


class WebhookAdmin(admin.ModelAdmin):
    list_display = ("name", "service", "url")


class ItemAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "description",
        "enabled",
        "requires_confirmation",
        "terms",
        "category",
    )


class ItemCategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)


class BlacklistedAdmin(admin.ModelAdmin):
    list_display = ("user", "time", "expires")


class ItemPoolItemAdmin(admin.ModelAdmin):
    list_display = ("name", "pool", "enabled", "priority", "status")


class ItemAccessoryAdmin(admin.ModelAdmin):
    list_display = ("name", "pool")


admin.site.register(Webhook, WebhookAdmin)
admin.site.register(ItemCategory, ItemCategoryAdmin)
admin.site.register(ItemPool, ItemAdmin)
admin.site.register(Booking, BookingAdmin)
admin.site.register(Blacklisted, BlacklistedAdmin)
admin.site.register(ItemPoolItem, ItemPoolItemAdmin)
admin.site.register(ItemPoolAccessory, ItemAccessoryAdmin)

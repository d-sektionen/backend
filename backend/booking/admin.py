from django.contrib import admin
from .models import Item, Booking, Blacklisted, ItemCategory


class BookingAdmin(admin.ModelAdmin):
    model = Booking
    list_display = (
        "user",
        "item",
        "start",
        "end",
        "description",
        "restricted_timeslot",
        "confirmed",
    )
    list_filter = (
        "item",
        "start",
        "end",
        "restricted_timeslot",
        "confirmed",
        ("user", admin.RelatedOnlyFieldListFilter),
    )
    search_fields = (
        "user__username",
        "user__first_name",
        "user__last_name",
        "description",
    )


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


admin.site.register(ItemCategory, ItemCategoryAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(Booking, BookingAdmin)
admin.site.register(Blacklisted, BlacklistedAdmin)

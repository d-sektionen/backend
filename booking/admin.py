from django.contrib import admin

from .models import Item, Booking


class BookingAdmin(admin.ModelAdmin):
    model = Booking
    list_display = ("user", "item", "start", "end", "description")
    list_filter = ("item", "start", "end", ("user", admin.RelatedOnlyFieldListFilter))
    search_fields = (
        "user__username",
        "user__first_name",
        "user__last_name",
        "description",
    )


class ItemAdmin(admin.ModelAdmin):
    list_display = ("name", "description")


admin.site.register(Item, ItemAdmin)
admin.site.register(Booking, BookingAdmin)

from django.contrib import admin

from .models import Item, Booking

class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'item', 'start', 'end', 'description')
    list_filter = ('item', ('user', admin.RelatedOnlyFieldListFilter))
    model = Booking

class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'description',)

admin.site.register(Item, ItemAdmin)
admin.site.register(Booking, BookingAdmin)

from django.contrib import admin

from storage.models import StorageRoom, Location, Booking, Object

class StorageRoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'longitude','latitude', 'description', 'model_url')

class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'room', 'description', 'can_contain_objects')

class BookingAdmin(admin.ModelAdmin):
    list_display = ('group', 'location', 'start_date','end_date', 'until_further_notice', 'description')

class ObjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'location','description', 'in_date', 'amount', 'belongs_to', 'private','can_be_borrowed')

admin.site.register(StorageRoom, StorageRoomAdmin)
admin.site.register(Location,LocationAdmin)
admin.site.register(Booking,BookingAdmin)
admin.site.register(Object,ObjectAdmin)
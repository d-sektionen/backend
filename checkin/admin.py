from django.contrib import admin

from .models import Event, Doorkeeper


class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'archived')


class DoorkeeperAdmin(admin.ModelAdmin):
    list_display = ('user', 'event')

admin.site.register(Event, EventAdmin)
admin.site.register(Doorkeeper, DoorkeeperAdmin)

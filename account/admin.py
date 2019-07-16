from django.contrib import admin

from .models import Profile

class ProfileAdmin(admin.ModelAdmin):
    readonly_fields = ('user',)
    list_display = ('user', 'liu_card_id',)

admin.site.register(Profile, ProfileAdmin)

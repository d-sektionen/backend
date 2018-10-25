from django.contrib import admin

from account.models import Section, Profile

class SectionAdmin(admin.ModelAdmin):
    list_display = ('name',)
    readonly_fields = ('user_group', 'admin_group')

admin.site.register(Section, SectionAdmin)

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('liu_card_id',)

admin.site.register(Profile, ProfileAdmin)

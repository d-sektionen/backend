from django.contrib import admin

from account.models import Section, Profile

class SectionAdmin(admin.ModelAdmin):
    list_display = ('name',)
    readonly_fields = ('user_group', 'admin_group',)

admin.site.register(Section, SectionAdmin)

class ProfileAdmin(admin.ModelAdmin):
    readonly_fields = ('user',)
    list_display = ('user', 'liu_card_id',)

admin.site.register(Profile, ProfileAdmin)

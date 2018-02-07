from django.contrib import admin

from account.models import Section


class SectionAdmin(admin.ModelAdmin):
    list_display = ('name',)
    readonly_fields = ('user_group', 'admin_group')


admin.site.register(Section, SectionAdmin)

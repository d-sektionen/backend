from django.contrib import admin

from .models import MailTemplate, Mail


class MailTemplateAdmin(admin.ModelAdmin):
    list_display = ("name",)


class MailAdmin(admin.ModelAdmin):
    list_display = ("subject", "category")


admin.site.register(Mail, MailAdmin)
admin.site.register(MailTemplate, MailTemplateAdmin)

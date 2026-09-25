from django.contrib import admin
from . import models


class OccurrenceInline(admin.StackedInline):
    model = models.Occurrence
    filter_horizontal = ("attendants",)


class OccurrenceAdmin(admin.ModelAdmin):
    list_display = ("name", "archived", "attendant_limit", "members_only", "clear_data")
    # inlines = [OccurrenceInline]


admin.site.register(models.Occurrence, OccurrenceAdmin)

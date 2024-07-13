from django.contrib import admin

from .models import Key, LogEntry

from django.utils.safestring import mark_safe


class KeyAdmin(admin.ModelAdmin):
    list_display = ("name", "order", "status", "colored_color")
    search_fields = ("name",)
    list_editable = ("order",)
    ordering = ("order",)
    # TODO: validate color!!
    def colored_color(self, obj):
        return mark_safe(
            f'<div style="display:inline-block;border-radius:3px;padding:3px;border: 3px solid {obj.color};">{obj.color}</div>'
        )

    colored_color.short_description = "color"


class LogEntryAdmin(admin.ModelAdmin):
    list_display = ("key", "taken_by", "taken_at", "returned_successfully")
    list_filter = (
        "key",
        "taken_at",
        "returned_at",
        "taken_successfully",
        "returned_successfully",
    )
    search_fields = (
        "taken_by__username",
        "taken_by__first_name",
        "taken_by__last_name",
        "returned_by__username",
        "returned_by__first_name",
        "returned_by__last_name",
    )


admin.site.register(Key, KeyAdmin)
admin.site.register(LogEntry, LogEntryAdmin)

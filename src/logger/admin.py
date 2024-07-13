from django.contrib import admin
from .models import Entry


class EntryAdmin(admin.ModelAdmin):
    list_display = ("category", "severity", "description", "user", "timestamp")
    list_filter = (
        "category",
        "severity",
        "timestamp",
        ("user", admin.RelatedOnlyFieldListFilter),
    )
    readonly_fields = ("category", "severity", "description", "user")
    search_fields = (
        "description",
        "user__username",
        "user__first_name",
        "user__last_name",
    )


admin.site.register(Entry, EntryAdmin)

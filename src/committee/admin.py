from django.contrib import admin

from ..committee.models import Committee, CommitteeMember


class CommitteeAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    ordering = ("name",)
    filter_horizontal = (
        "chairman_permissions",
        "treasurer_permissions",
        "other_permissions",
    )


admin.site.register(CommitteeMember)
admin.site.register(Committee, CommitteeAdmin)

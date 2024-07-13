from django.contrib import admin

from committee.forms import CommitteeForm
from committee.models import Committee


class CommitteeAdmin(admin.ModelAdmin):
    add_form = CommitteeForm
    change_form = CommitteeForm

    def get_form(self, request, obj=None, **kwargs):
        self.form = self.change_form if obj else self.add_form
        return super().get_form(request, obj, **kwargs)

    def get_fieldsets(self, request, obj=None, **kwargs):
        self.fieldsets = self.change_form.Meta.fieldsets if obj else self.add_form.Meta.fieldsets
        return super().get_fieldsets(request, obj, **kwargs)

    list_display = ("id", "name", "description", "treasurer", "treasurer_email",  "chair", "chair_email")
    list_filter = ("treasurer", "chair")
    search_fields = ("name", "description", "treasurer", "chair")
    ordering = ("name",)

admin.site.register(Committee, CommitteeAdmin)
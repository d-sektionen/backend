from django.contrib import admin

from committee.forms import CommitteeForm
from committee.models import Committee


class CommitteeAdmin(admin.ModelAdmin):
    add_form = CommitteeForm
    change_form = CommitteeForm

    def get_form(self, request, obj=None, **kwargs):
        if obj:
            self.form = self.change_form
        else:
            self.form = self.add_form
        return super().get_form(request, obj, **kwargs)

    list_display = 'id', 'name', 'description', 'contact',
    list_filter = 'contact',
    search_fields = 'name', 'description', 'contact',
    ordering = 'name',


admin.site.register(Committee, CommitteeAdmin)
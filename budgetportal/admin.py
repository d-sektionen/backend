from django.contrib import admin

from .models import BudgetEntry


class BudgetEntryAdmin(admin.ModelAdmin):
    list_display = ("user", "description", "date")
    search_fields = ("user__username",)
    ordering = ("-date",)


admin.site.register(BudgetEntry, BudgetEntryAdmin)

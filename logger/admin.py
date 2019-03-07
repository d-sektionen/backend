from django.contrib import admin
from .models import Entry

class EntryAdmin(admin.ModelAdmin):
  list_display = ('category', 'severity', 'description', 'user', 'timestamp')
  list_filter = ('category', 'severity', 'user', 'timestamp')
  readonly_fields = ('category', 'severity', 'description', 'user')
  search_fields = ('description',)

admin.site.register(Entry, EntryAdmin)
from django.contrib import admin
from django.db.models import QuerySet
from django.urls import reverse
from django.utils.html import format_html

from carlogging.models import LogEntry, LogStart


@admin.register(LogStart)
class LogStartAdmin(admin.ModelAdmin):
    list_display = (
        'id', 
        'logging_user', 
        'booking_user', 
        'link_to_log_entry',
        'link_to_car_booking', 
        'kilometers', 
        'car_cleaned',
        'logging_date',
    )
    ordering = ('logging_date',)

    list_filter = ('logging_user', 'booking_user',)
    search_fields = (
        'logging_user__username', 
        'logging_user__first_name', 
        'logging_user__last_name',
    )

    def link_to_car_booking(self, obj: LogStart):
        if obj.car_booking is None:
            return 'NULL'
        link = reverse('admin:booking_booking_change', args=[obj.car_booking.id])
        return format_html('<a href="{}">Car Booking ({})</a>', link, obj.car_booking.id)
    link_to_car_booking.short_description = 'Car Booking'

    def link_to_log_entry(self, obj: LogStart):
        if obj.log_entry is None:
            return 'NULL'
        link = reverse('admin:carlogging_logentry_change', args=[obj.log_entry.id])
        return format_html('<a href="{}">Log Entry ({})</a>', link, obj.log_entry.id)
    link_to_log_entry.short_description = 'Log Entry'
        

def mark_as_paid(modeladmin, request, queryset):
    for entry in queryset:
        entry.paid = True
        entry.save()
    modeladmin.message_user = 'Entries were successfully marked.'

mark_as_paid.short_description = "Mark selected entries as paid"


@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'logging_user',
        'link_to_log_start',
        'link_to_car_booking',
        'link_to_trailer_booking',
        'link_to_committee',
        'kilometers',
        'car_cleaned',
        'cost',
        'paid',
        'logging_date',
        'link_to_pdf',
    )
    ordering = ('logging_date',)

    list_filter = ('logging_user', 'booking_user', 'trailer_user',)
    search_fields = (
        'logging_user__username', 
        'logging_user__first_name', 
        'logging_user__last_name',
    )

    actions = [mark_as_paid]
    
    def link_to_log_start(self, obj: LogEntry):
        logging_user = obj.log_start.logging_user
        link = reverse('admin:carlogging_logstart_change', args=[obj.log_start.id])
        return format_html('<a href="{}">by {}</a>', link, logging_user.username)

    def link_to_car_booking(self, obj: LogEntry):
        car_booking = obj.log_start.car_booking
        if car_booking is None:
            return 'NULL'
        link = reverse('admin:booking_booking_change', args=[car_booking.id])
        return format_html('<a href="{}">by {}</a>', link, obj.booking_user.username)

    def link_to_trailer_booking(self, obj: LogEntry):
        if obj.trailer_booking is None:
            return 'NULL'
        link = reverse('admin:booking_booking_change', args=[obj.trailer_booking.id])
        return format_html('<a href="{}">by {}</a>', link, obj.trailer_user.username)

    def link_to_committee(self, obj: LogEntry):
        if obj.committee is None:
            return 'NULL'
        link = reverse('admin:committee_committee_change', args=[obj.committee.id])
        return format_html('<a href="{}">{}</a>', link, obj.committee.name)

    def link_to_pdf(self, obj: LogEntry):
        url = f'/carlogging/pdf-export/{obj.id}'
        return format_html('<a href="{}">Export to PDF</a>', url)

    link_to_log_start.short_description = 'Log Start'
    link_to_car_booking.short_description = 'Car Booking'
    link_to_trailer_booking.short_description = 'Trailer Booking'
    link_to_committee.short_description = 'Committee'
    link_to_pdf.short_description = 'Export to PDF'

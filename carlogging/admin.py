from django.contrib import admin

from account import models
from .models import LogEntry, LogStart

from django.urls import reverse
from django.utils.html import format_html


@admin.register(LogStart)
class LogStartAdmin(admin.ModelAdmin):
    model = LogStart
    list_display = (
        'id',
        'logging_user',
        'booking_user',
        'link_to_car_booking',
        'kilometers',
        # 'message',
        'car_cleaned',
        'logging_finished',
        'logging_date'
    )
    list_filter = ('logging_user', 'booking_user')
    search_fields = (
        'logging_user__username', 
        'logging_user__first_name', 
        'logging_user__last_name'
    )

    def link_to_car_booking(self, obj):
        if obj.car_booking is None:
            return 'NULL'
        link = reverse('admin:booking_booking_change', args=[obj.car_booking.id])
        return format_html('<a href="{}">Booking ({})</a>', link, obj.car_booking.id)
    link_to_car_booking.short_description = 'Car Booking'


@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    model = LogEntry
    list_display = (
        'id',
        'logging_user',
        'booking_user',
        'link_to_pdf',
        'link_to_logstart',
        'kilometers',
        # 'message',
        'car_cleaned',
        'logging_date',
        'car_days',
        'trailer_user',
        'link_to_trailer_booking',
        'trailer_days',
        'cost',
        'paid'
    )
    list_filter = ('logging_user', 'booking_user', 'trailer_user')
    search_fields = (
        'logging_user__username', 
        'logging_user__first_name', 
        'logging_user__last_name'
    )

    def link_to_pdf(self, obj):
        url = f'/carlogging/pdf-export/{obj.id}'
        return format_html('<a href="{}">Export to PDF</a>', url)
    link_to_pdf.short_description = 'Export to PDF'
    
    def link_to_logstart(self, obj):
        link = reverse('admin:carlogging_logstart_change', args=[obj.log_start.id])
        return format_html('<a href="{}">{}</a>', link, obj.log_start)
    link_to_logstart.short_description = 'Belongs to'

    def link_to_trailer_booking(self, obj):
        if obj.trailer_booking is None:
            return 'NULL'
        link = reverse('admin:booking_booking_change', args=[obj.trailer_booking.id])
        return format_html('<a href="{}">Booking ({})</a>', link, obj.trailer_booking.id)
    link_to_trailer_booking.short_description = 'Trailer Booking'

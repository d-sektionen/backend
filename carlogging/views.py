from django.shortcuts import render
from django.utils import timezone

from account import serializers
from booking.models import Booking
from .models import LogEntry, LogStart, CAR_DAILY_COST, TRAILER_DAILY_COST, COST_PER_KM
from rest_framework import viewsets, mixins, status
from .serializers import LogEntrySerializer, LogStartSerializer
from .permissions import LoggingAdminPermissions, LoggingPermissions
from .utils import validate_booking_user, get_booking, validate_start_data, validate_entry_data
from rest_framework.response import Response
from django.db.models import F, Q
from django.contrib.auth.models import User
from membership.utils import check_membership
from rest_framework.views import APIView
from django.http import FileResponse
import io
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from datetime import datetime


class LogStartViewSet(
    mixins.ListModelMixin,
    # mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = LogStartSerializer
    permission_classes = (LoggingPermissions,)
    queryset = LogStart.objects.all()

    def get_queryset(self):
        return LogStart.objects.filter(
            Q(logging_user=self.request.user) |
            Q(booking_user=self.request.user)
        )

    def create(self, request):
        data = request.data
        data_resp = validate_start_data(data)
        if data_resp:
            return data_resp

        booking_user_id = data['booking_liu_id']
        booking_user_resp = validate_booking_user(booking_user_id)
        if booking_user_resp:
            return booking_user_resp
        booking = get_booking(booking_user_id)

        booking_user = User.objects.get(username=booking_user_id)
        if LogStart.objects.filter(
            booking_user=booking_user,
            logging_finished=False
        ).exists():
            return Response(
                {'error': f'A LogStart object has already been created for "{booking_user_id}"!',
                 'status_text': f'Det finns redan en oavslutad, påbörjad loggning för "{booking_user_id}"!'},
                status.HTTP_400_BAD_REQUEST
            )
            
        LogStart.objects.create(
            logging_user=request.user,
            booking_user=booking_user,
            car_booking=booking,
            kilometers=data['kilometers'],
            message=data['message'],
            car_cleaned=data['car_cleaned']
        )

        # booking.is_logged = True
        # booking.save()

        return Response(
            {'status_text': 'Loggningen är nu påbörjad.'},
            status.HTTP_200_OK
        )


class LogEntryViewSet(
    mixins.ListModelMixin,
    # mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = LogEntrySerializer
    permission_classes = (LoggingPermissions,)
    queryset = LogEntry.objects.all()

    def get_queryset(self):
        entries = LogEntry.objects.filter(
            Q(logging_user=self.request.user) |
            Q(booking_user=self.request.user)
        )
        for entry in entries:
            if entry.log_start.logging_user != self.request.user:
                # Hide the "personal data" of the person who created the
                # log_start, from the requesting user
                entry.log_start.logging_user = None
                entry.log_start.message = None
        return entries

    def create(self, request):
        data = request.data
        data_resp = validate_entry_data(data)
        if data_resp:
            return data_resp

        if data['trailer']:
            trailer_user_id = data['booking_liu_id']  # TODO: data['trailer_liu_id']
            trailer_user_resp = validate_booking_user(trailer_user_id, check_for_trailer=True)
            if trailer_user_resp:
                return trailer_user_resp

        booking_user_id = data['booking_liu_id']
        booking_user = User.objects.get(username=booking_user_id)
        log_start = LogStart.objects.filter(
            booking_user=booking_user, 
            logging_finished=False
        ).first()

        if log_start is None:
            return Response(
                {'error': f'No LogStart object has been created for "{booking_user_id}"!',
                 'status_text': 'Du måste påbörja en loggning innan du kan avsluta den!'},
                status.HTTP_404_NOT_FOUND
            )

        if log_start.kilometers >= data['kilometers']:
            return Response(
                {'error': 'Start kilometer should be less than end kilometer!',
                 'status_text': f'Mätarställningen som anges måste vara större än när loggningen startades, då angavs {log_start.kilometers} km.'},
                status.HTTP_400_BAD_REQUEST
            )

        # Calculate amount of days car has been used
        if log_start.car_booking.end >= timezone.now():
            car_timedelta = timezone.now() - log_start.car_booking.start
        else:
            car_timedelta = log_start.car_booking.end - log_start.car_booking.start
        car_days = max(1, car_timedelta.days)

        # Calculate amount of days trailer has been used
        if data['trailer']:
            trailer_booking = get_booking(trailer_user_id, check_for_trailer=True)
            if trailer_booking.end >= timezone.now():
                trailer_timedelta = timezone.now() - trailer_booking.start
            else:
                trailer_timedelta = trailer_booking.end - trailer_booking.start
            trailer_days = max(1, trailer_timedelta.days)
        else:
            trailer_booking = None
            trailer_days = 0

        log_entry = LogEntry.objects.create(
            logging_user=request.user,
            booking_user=booking_user,
            log_start=log_start,
            kilometers=data['kilometers'],
            message=data['message'],
            car_cleaned=data['car_cleaned'],
            car_days=car_days,
            trailer_booking=trailer_booking,
            trailer_days=trailer_days
        )
        log_entry.cost = log_entry.calc_cost()
        log_entry.save()

        log_start.logging_finished = True
        log_start.save()

        if log_start.car_booking.end >= timezone.now():
            log_start.car_booking.end = timezone.now()
            log_start.car_booking.save()

        if trailer_booking is not None:
            # trailer_booking.is_logged = True
            if trailer_booking.end >= timezone.now():
                trailer_booking.end = timezone.now()
                trailer_booking.save()
            trailer_booking.save()

        return Response(
            {'status_text': 'Loggningen är nu avslutad!'},
            status.HTTP_200_OK
        )


class PdfExport(APIView):
    permisson_classes = (LoggingAdminPermissions,)

    def get(self, request, *args, **kwargs):
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter, bottomup=0)

        # print(c.getAvailableFonts())

        log_entry_id = self.kwargs['entry_id']
        log_entry = LogEntry.objects.get(pk=log_entry_id)

        textobj = c.beginText()
        textobj.setTextOrigin(inch, inch)
        textobj.setFont('Courier', 18)
        textobj.textLine(f'Billoggning (id: {log_entry_id})')

        lines = [
            ('Starttid (startloggning):', str(log_entry.log_start.logging_date).split('.')[0]),
            ('Sluttid (slutloggning):', str(log_entry.logging_date).split('.')[0]),
            ('LiU-ID på bokningen:', log_entry.booking_user.username),
            ('Start:', f'{log_entry.log_start.kilometers} km'),
            ('Stopp:', f'{log_entry.kilometers} km'),
            '-'*64,
            ('Pris per kilometer:', f'{COST_PER_KM} kr/km'),
            ('Antal km:', f'{log_entry.kilometers - log_entry.log_start.kilometers} km'),
            ('Dygn med bil:', log_entry.car_days),
            (
                'Dygnshyra:',
                f'{(log_entry.car_days - 1) * CAR_DAILY_COST} kr    ({CAR_DAILY_COST}kr/dygn efter första)'
            )
        ]

        if log_entry.trailer_booking is not None:
            lines += [
                ('Dygn med släp:', log_entry.trailer_days),
                (
                    'Släpdygnshyra:',
                    f'{log_entry.trailer_days * TRAILER_DAILY_COST} kr    ({TRAILER_DAILY_COST}kr/dygn)'
                )
            ]

        lines += [
            '-'*64,
            ('Summa:', f'{log_entry.cost} kr'),
            '',
            ('Denna PDF skapades:', str(datetime.now()).split('.')[0])
        ]

        # Apply lines to text object
        LEFT_COLUMN_LEN = 30
        textobj.setFont('Courier', 12)
        for line in lines:
            if isinstance(line, tuple):
                left = line[0]
                right = line[1]

                if len(left) < LEFT_COLUMN_LEN:
                    left += ' '*(LEFT_COLUMN_LEN - len(left))

                line = f'{str(left) + str(right)}'
            textobj.textLine(line)

        c.drawText(textobj)
        c.showPage()
        c.save()
        buffer.seek(0)

        return FileResponse(buffer, as_attachment=False, filename='car-logging.pdf')

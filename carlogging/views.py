from django.contrib.auth.models import User
from django.db.models import Q
from django.http import FileResponse
from django.utils import timezone
from rest_framework import status, viewsets, mixins
from rest_framework.decorators import api_view, permission_classes
from rest_framework.request import Request
from rest_framework.response import Response

from io import BytesIO
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch

from carlogging.models import LogStart, LogEntry, CAR_DAILY_COST, TRAILER_DAILY_COST, COST_PER_KM
from carlogging.permissions import LoggingPermissions, LoggingAdminPermissions
from carlogging.serializers import LogStartSerializer, LogEntrySerializer
from carlogging.utils import get_unlogged_booking, validate_request_data
from committee.models import Committee


class LogStartViewSet(mixins.RetrieveModelMixin,
                      mixins.ListModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    queryset = LogStart.objects.all()
    serializer_class = LogStartSerializer
    permission_classes = (LoggingPermissions,)

    def get_queryset(self):
        return LogStart.objects.filter(
            Q(logging_user=self.request.user) |
            Q(car_user=self.request.user))

    def create(self, request: Request):
        """
        Creates a new LogStart object, if the booker has an unlogged car booking
        and no unfinished logs.
        """
        data_types = {'car_liu_id': str,
                      'kilometers': int,
                      'message': str,
                      'car_cleaned': bool}
        data_resp = validate_request_data(request.data, data_types)
        if data_resp: 
            return data_resp
        
        # Validate the car booker and booking
        car_liu_id = request.data['car_liu_id']
        car_user = User.objects.filter(username=car_liu_id).first()
        if car_user is None:
            return Response({'status_text': f'Ingen användare med LiU-ID:t {car_liu_id} finns'},
                            status.HTTP_404_NOT_FOUND)

        # TODO: skulle vara bättre att implementera i bokningsappen
        if not car_user.committees.exists():
            return Response({'status_text': f'{car_liu_id} måste vara sektionsaktiv för att boka bil'},
                            status.HTTP_403_FORBIDDEN)

        if LogStart.objects.filter(car_user=car_user, log_entry=None).exists():
            return Response({'status_text': f'En oavslutad loggning för {car_liu_id} finns redan'},
                            status.HTTP_409_CONFLICT)

        car_booking = get_unlogged_booking(car_user, False)
        if car_booking is None:
            return Response({'status_text': f'Ingen ologgad bilbokning av {car_liu_id} finns'},
                            status.HTTP_404_NOT_FOUND)

        # Start a new log
        LogStart.objects.create(logging_user=request.user,
                                car_user=car_user,
                                car_booking=car_booking,
                                kilometers=request.data['kilometers'],
                                message=request.data['message'],
                                car_cleaned=request.data['car_cleaned'])
        return Response({'status_text': 'Loggningen är nu påbörjad'},
                        status.HTTP_201_CREATED)


class LogEntryViewSet(mixins.RetrieveModelMixin,
                      mixins.ListModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    queryset = LogEntry.objects.all()
    serializer_class = LogEntrySerializer
    permission_classes = (LoggingPermissions,)

    def get_queryset(self):
        entries = LogEntry.objects.filter(
            Q(logging_user=self.request.user) |
            Q(car_user=self.request.user))
        for entry in entries:
            if entry.log_start.logging_user != self.request.user:
                # Hide the "personal data" of the person who created the
                # log_start, from the requesting user
                entry.log_start.logging_user = None
                entry.log_start.message = None
        return entries

    def create(self, request: Request):
        """
        Creates a new LogStart object, if the booker has an unlogged car booking
        and no unfinished logs.
        """
        data_types = {'car_liu_id': str,
                      'trailer': bool,
                      'trailer_liu_id': str,
                      'committee_id': int,
                      'kilometers': int,
                      'message': str,
                      'car_cleaned': bool}
        data_resp = validate_request_data(request.data, data_types)
        if data_resp: 
            return data_resp

        # Validate the car booker and log start
        car_liu_id = request.data['car_liu_id']
        car_user = User.objects.filter(username=car_liu_id).first()
        if car_user is None:
            return Response({'status_text': f'Ingen användare med LiU-ID:t {car_liu_id} finns'},
                            status.HTTP_404_NOT_FOUND)
                            
        # TODO: skulle vara bättre att implementera i bokningsappen
        if not car_user.committees.exists():
            return Response({'status_text': f'{car_liu_id} måste vara sektionsaktiv för att boka bil'},
                            status.HTTP_403_FORBIDDEN)

        log_start = LogStart.objects.filter(car_user=car_user, log_entry=None).first()
        if log_start is None:
            return Response({'status_text': f'Ingen oavslutad loggning för {car_liu_id} hittades'},
                            status.HTTP_404_NOT_FOUND)

        # Validate the trailer booker and booking
        if request.data['trailer']:
            trailer_liu_id = request.data['trailer_liu_id']
            trailer_user = User.objects.filter(username=trailer_liu_id).first()
            if trailer_user is None:
                return Response({'status_text': f'Ingen användare med LiU-ID:t {trailer_liu_id} finns'},
                                status.HTTP_404_NOT_FOUND)

            # TODO: skulle vara bättre att implementera i bokningsappen
            if not trailer_user.committees.exists():
                return Response({'status_text': f'{trailer_liu_id} måste vara sektionsaktiv för att boka släp'},
                                status.HTTP_403_FORBIDDEN)

            trailer_booking = get_unlogged_booking(trailer_user, True)
            if trailer_booking is None:
                return Response({'status_text': f'Ingen ologgad släpbokning av {trailer_liu_id} finns'},
                                status.HTTP_404_NOT_FOUND)
        else:
            trailer_user = None
            trailer_booking = None

        # Validate the rest of the request data
        committee = Committee.objects.filter(id=request.data['committee_id']).first()
        if committee is None:
            return Response({'status_text': 'Det valda utskottet finns inte'},
                            status.HTTP_404_NOT_FOUND)

        if log_start.kilometers >= request.data['kilometers']:
            return Response({'status_text': f'Antalet kilometer måste vara större än när loggningen \
                             startades ({log_start.kilometers})'},
                            status.HTTP_400_BAD_REQUEST)

        # Calculate cost of bookings and finish the log
        if log_start.car_booking.end >= timezone.now():
            car_timedelta = timezone.now() - log_start.car_booking.start
        else:
            car_timedelta = log_start.car_booking.end - log_start.car_booking.start
        car_days = max(1, car_timedelta.days)

        if request.data['trailer']:
            if trailer_booking.end >= timezone.now():
                trailer_timedelta = timezone.now() - trailer_booking.start
            else:
                trailer_timedelta = trailer_booking.end - trailer_booking.start
            trailer_days = max(1, trailer_timedelta.days)
        else:
            trailer_days = 0

        entry = LogEntry.objects.create(logging_user=request.user,
                                        car_user=car_user,
                                        trailer_user=trailer_user,
                                        trailer_booking=trailer_booking,
                                        log_start=log_start,
                                        committee=committee,
                                        car_days=car_days,
                                        trailer_days=trailer_days,
                                        kilometers=request.data['kilometers'],
                                        message=request.data['message'],
                                        car_cleaned=request.data['car_cleaned'])
        entry.cost = entry.calc_cost()
        entry.save()

        # Cutoff booking end times to allow for new bookings
        if log_start.car_booking.end >= timezone.now():
            log_start.car_booking.end = timezone.now()
            log_start.car_booking.save()
        
        if request.data['trailer'] and trailer_booking.end >= timezone.now():
            trailer_booking.end = timezone.now()
            trailer_booking.save()
        
        return Response({'status_text': 'Loggningen är nu avslutad'},
                        status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([LoggingAdminPermissions])
def export_entry_pdf(request: Request, entry_id: int):
    """Generates a PDF outlining the details of the specified LogEntry object."""

    entry = LogEntry.objects.filter(id=entry_id).first()
    if entry is None:
        return Response({'status_text': f'Ingen loggning med ID:t {entry_id} finns'},
                        status.HTTP_404_NOT_FOUND)

    buffer = BytesIO()
    canvas = Canvas(buffer, pagesize=letter, bottomup=0)
    text = canvas.beginText()

    text.setTextOrigin(inch, inch)
    text.setFont('Courier', 18)
    text.textLine(f'Billoggning (id: {entry_id})')

    lines = [
        ('Starttid (startloggning):', str(entry.log_start.logging_date).split('.')[0]),
        ('Sluttid (slutloggning):', str(entry.logging_date).split('.')[0]),
        ('LiU-ID på bokningen:', entry.car_user.username),
        ('Start:', f'{entry.log_start.kilometers} km'),
        ('Stopp:', f'{entry.kilometers} km'),
        '-'*64,
        ('Pris per kilometer:', f'{COST_PER_KM} kr/km'),
        ('Antal km:', f'{entry.kilometers - entry.log_start.kilometers} km'),
        ('Dygn med bil:', entry.car_days),
        ('Dygnshyra:', f'{(entry.car_days - 1) * CAR_DAILY_COST} kr    ({CAR_DAILY_COST}kr/dygn efter första)')
    ]

    if entry.trailer_booking is not None:
        lines += [
            ('Dygn med släp:', entry.trailer_days),
            ('Släpdygnshyra:', f'{entry.trailer_days * TRAILER_DAILY_COST} kr    ({TRAILER_DAILY_COST}kr/dygn)')
        ]

    lines += [
        '-'*64,
        ('Summa:', f'{entry.cost} kr'),
        '',
        ('Denna PDF skapades:', str(timezone.now()).split('.')[0])
    ]

    # Apply lines to text object
    LEFT_COLUMN_LEN = 30
    text.setFont('Courier', 12)
    for line in lines:
        if isinstance(line, tuple):
            left, right = line
            
            if len(left) < LEFT_COLUMN_LEN:
                left += ' ' * (LEFT_COLUMN_LEN - len(left))

            line = f'{str(left) + str(right)}'
        text.textLine(line)

    canvas.drawText(text)
    canvas.showPage()
    canvas.save()
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=False, filename=f'car-logging-{entry_id}.pdf')

from django.shortcuts import render
from .models import LogEntry, LogStart, DAILY_COST, TRAILER_DAILY_COST
from rest_framework import viewsets, mixins, status
from .serializers import LogEntrySerializer, LogStartSerializer
from .permissions import LoggingAdminPermissions, LoggingPermissions
from .utils import check_invalid_booking
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
        entries = LogEntry.objects.filter(  # filter matching logging_user OR booking_liu_id
            Q(logging_user=self.request.user) |
            Q(booking_user=self.request.user)
        )
        for entry in entries:
            if entry.log_start.logging_user != self.request.user:
                # hide the "personal data" of the person who created the
                # log_start, from the requesting user:
                entry.log_start.logging_user = None
                entry.log_start.start_message = None
        return entries

    def create(self, request):
        error_response = check_invalid_booking(request.data)
        if error_response:
            return error_response

        log_start_exists = LogStart.objects.filter(
            booking_user=User.objects.get(
                username=request.data["booking_liu_id"]),
            logging_finished=False
        ).exists()
        if not log_start_exists:
            return Response(
                {"error": "No LogStart object has been created for this booking",
                 "status_text": "Du måste påbörja en loggning innan du kan avsluta den."},
                status=status.HTTP_404_NOT_FOUND
            )

        log_start_obj = LogStart.objects.get(
            booking_user=User.objects.get(
                username=request.data["booking_liu_id"]),
            logging_finished=False
        )
        if log_start_obj.start_km >= request.data["end_km"]:
            return Response(
                {"error": "Start kilometer should be less than end kilometer",
                 "status_text": f"Mätarställningen som anges måste vara större än när loggningen startades, då angavs {log_start_obj.start_km} km."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if request.data["trailer_days"] == None:
            request.data["trailer_days"] = 1
        if request.data["car_days"] == None:
            request.data["car_days"] = 1
        if request.data["trailer_days"] < 1:
            return Response(
                {"error": "Days trailer is rented can't be less than 1!",
                 "status_text": "Antalet dagar för släpet får ej vara mindre än 1"},
                status=status.HTTP_400_BAD_REQUEST
            )
        if request.data["car_days"] < 1:
            return Response(
                {"error": "Days car is rented can't be less than 1!",
                 "status_text": "Antalet dagar för bilen får ej vara mindre än 1"},
                status=status.HTTP_400_BAD_REQUEST
            )

        log_entry = LogEntry.objects.create(
            log_start=log_start_obj,
            car_days=request.data["car_days"],
            logging_user=request.user,
            booking_user=User.objects.get(
                username=request.data["booking_liu_id"]
            ),
            trailer=request.data["trailer"],
            trailer_days=request.data["trailer_days"],
            active_member=request.data["active_member"],
            member=check_membership(
                request.data["booking_liu_id"]
            ),
            end_message=request.data["end_message"],
            end_km=request.data["end_km"],
            end_car_cleaned=request.data["end_car_cleaned"],
        )
        log_entry.cost = log_entry.calc_cost()
        log_entry.save()

        log_start_obj.logging_finished = True
        log_start_obj.save()

        return Response(
            {"status": "ok",
             "status_text": "Loggningen är nu avslutad."},
            status=status.HTTP_200_OK
        )


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
        return LogStart.objects.filter(  # filter matching logging_user OR booking_liu_id
            Q(logging_user=self.request.user) |
            Q(booking_user=self.request.user)
        )

    def create(self, request):
        error_response = check_invalid_booking(request.data)
        if error_response:
            return error_response

        if LogStart.objects.filter(
            booking_user=User.objects.get(
                username=request.data["booking_liu_id"]),
            logging_finished=False
        ).exists():
            return Response(
                {"error": "A LogStart object has already been created for this user",
                 "status_text": "Det finns redan en påbörjad loggning för den här användaren, du måste avsluta den först."},
                status=status.HTTP_400_BAD_REQUEST
            )

        LogStart.objects.create(
            logging_user=request.user,
            booking_user=User.objects.get(
                username=request.data["booking_liu_id"]),
            start_km=request.data["start_km"],
            start_message=request.data["start_message"],
            start_car_cleaned=request.data["start_car_cleaned"],
            logging_finished=False,
        )

        return Response(
            {"status": "ok",
             "status_text": "Loggningen är nu påbörjad."},
            status=status.HTTP_200_OK
        )


class PdfExport(APIView):
    permission_classes = (LoggingAdminPermissions,)

    def get(self, request, *args, **kwargs):
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter, bottomup=0)

        # print(c.getAvailableFonts())

        textobj = c.beginText()
        textobj.setTextOrigin(inch, inch)
        textobj.setFont("Courier", 18)

        log_entry_id = self.kwargs["entry_id"]
        textobj.textLine(f"Billoggning (id: {log_entry_id})")

        data = LogEntry.objects.get(pk=log_entry_id)

        username = data.booking_user.username
        cost_type = "Sektionsaktiv 3 kr/km" if data.active_member else (
            "Sektionsmedlem 4 kr/km" if check_membership(username) else (
                "Ej sektionsmedlem 6 kr/km"
            )
        )

        lines = [
            ("Starttid (startloggning):", str(data.log_start.logging_date).split('.')[0]),
            ("Sluttid (slutloggning):", str(data.logging_date).split('.')[0]),
            ("LiU-ID på bokningen:", username),
            ("Start:", f"{data.log_start.start_km} km"),
            ("Stopp:", f"{data.end_km} km"),
            "-"*60,
            ("Prisklass:", cost_type),
            ("Antal km:", f"{data.end_km - data.log_start.start_km} km"),
            ("Påbörjade dygn:", data.car_days),
            (
                "Dygnshyra:",
                f"{(data.car_days - 1) * DAILY_COST} kr    ({DAILY_COST}kr/dygn efter första)"
            ),
            ("Dygn med släp:", data.trailer_days),
            (
                "Släpdygnshyra:",
                f"{data.trailer_days * TRAILER_DAILY_COST} kr    ({TRAILER_DAILY_COST}kr/dygn)"
            ),
            "-"*60,
            ("Summa:", f"{data.cost} kr"),
            "",
            ("Denna PDF skapades:", str(datetime.now()).split(".")[0]),
        ]

        LEFT_COLUMN_LEN = 30
        textobj.setFont("Courier", 12)
        for line in lines:
            if isinstance(line, tuple):
                left = line[0]
                right = line[1]

                if len(left) < LEFT_COLUMN_LEN:
                    left += ' '*(LEFT_COLUMN_LEN - len(left))

                line = f"{str(left) + str(right)}"
            textobj.textLine(line)

        c.drawText(textobj)
        c.showPage()
        c.save()
        buffer.seek(0)

        return FileResponse(buffer, as_attachment=False, filename="car-logging.pdf")

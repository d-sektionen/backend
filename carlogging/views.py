from django.shortcuts import render
from .models import LogEntry, LogStart
from rest_framework import viewsets, mixins, status
from .serializers import LogEntrySerializer, LogStartSerializer
from .permissions import LoggingPermissions
from .utils import check_invalid_booking
from rest_framework.response import Response
from django.db.models import F, Q
from django.contrib.auth.models import User


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
        return LogEntry.objects.filter(  # filter matching logging_user OR booking_liu_id
            Q(logging_user=self.request.user) |
            Q(booking_user=self.request.user)
        )

    def create(self, request):
        error_response = check_invalid_booking(request.data)
        if error_response:
            return error_response

        log_start_exists = LogStart.objects.filter(
            booking_user=User.objects.get(username=request.data["booking_liu_id"]),
            logging_finished=False
        ).exists()
        if not log_start_exists:
            return Response(
                {"error": "No LogStart object has been created for this booking",
                "status_text": "Du måste påbörja en loggning innan du kan avsluta den."}, 
                status=status.HTTP_404_NOT_FOUND
            )

        log_start_obj = LogStart.objects.get(
            booking_user=User.objects.get(username=request.data["booking_liu_id"]), 
            logging_finished=False
        )
        if log_start_obj.start_km >= request.data["end_km"]:
            return Response(
                {"error": "Start kilometer should be less than end kilometer",
                "status_text" : f"Mätarställningen som anges måste vara större än när loggningen startades, då angavs {log_start_obj.start_km} km."}, 
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
            booking_user=User.objects.get(username=request.data["booking_liu_id"]),
            trailer=request.data["trailer"],
            trailer_days=request.data["trailer_days"],
            active_member=request.data["active_member"],
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
            "status_text" : "Loggningen är nu avslutad."}, 
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
            booking_user=User.objects.get(username=request.data["booking_liu_id"]),
            logging_finished=False
        ).exists():
            return Response(
                {"error": "A LogStart object has already been created for this user", 
                "status_text" : "Det finns redan en påbörjad loggning för den här användaren, du måste avsluta den först."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        LogStart.objects.create(
            logging_user=request.user,
            booking_user=User.objects.get(username=request.data["booking_liu_id"]),
            start_km=request.data["start_km"],
            start_message=request.data["start_message"],
            start_car_cleaned=request.data["start_car_cleaned"],
            logging_finished=False,
        )

        return Response(
            {"status": "ok",
            "status_text" : "Loggningen är nu påbörjad."}, 
            status=status.HTTP_200_OK
        )


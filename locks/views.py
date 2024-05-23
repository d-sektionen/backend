from rest_framework.decorators import (
    action,
)
from rest_framework import viewsets
from rest_framework.response import Response
import datetime
from rest_framework import status
from django.conf import settings
from seamapi.types import SeamApiException
from account.permissions import AllowMembers
from logger.utils import log, Entry
from seamapi import Seam

SEAM_BETTAN_ID = settings.SEAM_BETTAN_ID
seam = Seam()


class BettanViewSet(viewsets.ViewSet):
    permission_classes = (AllowMembers,)

    def list(self, request):
        lock = None
        try:
            lock = seam.locks.get(device=SEAM_BETTAN_ID)
        except SeamApiException as e:
            if e.metadata is None:
                return Response(
                    {"detail": "Något gick fel. Kontakta Webmaster."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            if e.metadata["type"] and e.metadata["type"] == "device_not_found":
                return Response(
                    {"detail": "Det gick inte att hitta låset. Kontakta Webmaster."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            return Response(
                {"detail": "Något gick fel. Kontakta Webmaster."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        if lock.errors:
            formatted_errors = []
            for error in lock.errors:
                if error["error_code"] == "device_disconnected":
                    formatted_errors.append("Kan inte kommunicera med låset. Är den bortkopplad?")
                elif error["error_code"] == "hub_disconnected":
                    formatted_errors.append("Kan inte kommunicera med hubben. Är den bortkopplad?")

            return Response(
                {"detail": "\n".join(formatted_errors)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {
                "status": lock.properties.online,
                "battery_percentage": lock.properties.battery_level * 100,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["post"])
    def unlock(self, request):
        return self.lock_command("unlock", request.user)

    @action(detail=False, methods=["post"])
    def lock(self, request):
        return self.lock_command("lock", request.user)

    def lock_command(self, command, user):
        """
        Unlocks or locks the Bettan door.
        """
        now = datetime.datetime.now()

        # Limit time of day when people can unlock door, they should still be able to lock at any time.
        todayMorningLimit = now.replace(hour=5, minute=0, second=0, microsecond=0)
        todayEveningLimit = now.replace(hour=21, minute=0, second=0, microsecond=0)
        notWithinLimits = now > todayEveningLimit or now < todayMorningLimit

        if command == "unlock" and notWithinLimits:
            return Response(
                {
                    "detail": "Det går endast att låsa upp mellan "
                    + todayMorningLimit.strftime("%H:%M")
                    + " och "
                    + todayEveningLimit.strftime("%H:%M")
                    + "."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Log action and send request
        if not log(command, Entry.NETLIGHT, user=user):
            return Response(
                {"detail": "Unable to log request."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # An action attempt may not always be successful and may need polling.
        # If errors start occurring, look into that.
        attempt = None
        if command == "unlock":
            attempt = seam.locks.unlock_door(device=SEAM_BETTAN_ID)
        elif command == "lock":
            attempt = seam.locks.lock_door(device=SEAM_BETTAN_ID)
        else:
            return Response({"detail": "Invalid command."}, status=status.HTTP_400_BAD_REQUEST)

        # Respond to success
        if attempt.status == "success":
            msg = "upplåst" if command == "unlock" else "låst"
            return Response(
                {"detail": "Dörren är nu på väg att bli " + msg + "."},
                status=status.HTTP_200_OK,
            )
        # TODO: There might me more errors to handle but the Seam error documentation is not great.

        # If all other checks fail.
        return Response(
            {"detail": "Problem i kommunikationen med låset.", "status": "500"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

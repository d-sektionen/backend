from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import redirect
from django.conf import settings
from django_ical.views import ICalFeed
from django.utils.timezone import get_current_timezone
from rest_framework import mixins, viewsets, status
from rest_framework.decorators import list_route, action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from app.permissions import FixedDjangoModelPermissions
from booking.models import Booking


from .serializers import (
    UserSerializer,
    SimpleUserSerializer,
    InfomailUserSerializer,
    CalendarSubscriptionSerializer,
)
from .permissions import IsUser
from .idtoken import generate_id_token, read_id_token
from .models import CalendarSubscription


@login_required
def generate_token(request):
    refresh = RefreshToken.for_user(request.user)

    if "redirect" in request.GET:
        redirect_url = request.GET["redirect"]
        querystring = "access=" + str(refresh.access_token) + "&refresh=" + str(refresh)

        return redirect(
            redirect_url + ("&" if "?" in redirect_url else "?") + querystring
        )
    else:
        return JsonResponse(
            {"refresh": str(refresh), "access": str(refresh.access_token)}
        )


class UserViewSet(
    mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet
):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = (
        IsUser,
    )  # Add IsAdminUser too if you want, not really needed though

    def get_object(self):
        return self.request.user if self.kwargs["pk"] == "me" else super().get_object()

    @action(detail=False, methods=["get", "post"], permission_classes=(IsUser,))
    def identification_token(self, request):
        """
        Returns a jwt token, for identifying a user, NOT to be used for auth.

        Currently used to enable user identifying QR codes for the checkin app.
        (The QR codes are generated and read client side)
        """
        if request.method == "GET":
            token = generate_id_token(request.user)
            return Response({"token": token}, status.HTTP_200_OK)
        elif request.method == "POST":
            # TODO: validate that token param exists
            user = read_id_token(request.data["token"])
            return Response(SimpleUserSerializer(user).data, status.HTTP_200_OK)

    @action(
        detail=False, methods=["get"], permission_classes=[FixedDjangoModelPermissions]
    )
    def infomail_subscribers(self, request):
        """
        Returns all users who are infomail subscribers.
        """
        users = User.objects.filter(profile__infomail_subscriber=True)
        return Response(
            InfomailUserSerializer(users, many=True).data, status.HTTP_200_OK
        )


class CalendarSubscriptionViewSet(viewsets.ModelViewSet):
    queryset = CalendarSubscription.objects.all()
    serializer_class = CalendarSubscriptionSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return CalendarSubscription.objects.filter(user=self.request.user)


class CalendarFeed(ICalFeed):
    """
    A calendar
    """

    product_id = "-//d-sektionen.se//calendar//SV"
    timezone = str(get_current_timezone())
    file_name = "d-sektionen.ics"
    title = "D-sektionen kalender"

    def get_object(self, request, pk):
        return CalendarSubscription.objects.get(pk=pk)

    def description(self, subscription):
        features = []
        if subscription.include_bookings:
            features.append("bokningar från bokningssystemet")
        if subscription.include_events_attending:
            features.append("evenemang du är registrerad på")
        if subscription.include_events_not_attending:
            features.append("evenemang du inte är registrerad på")
        features_string = "ingenting" if len(features) == 0 else ", ".join(features)
        return f"Kalender för tjänster på D-sektionens medlemsportal. Prenumerationen innehåller {features_string}."

    def items(self, subscription):
        items = []
        if subscription.include_bookings:
            bookings = [
                {
                    "id": f"booking-{b.id}",
                    "start": b.start,
                    "end": b.end,
                    # TODO extend with link etc
                    "description": b.description,
                    "title": f"Bokning av {b.item.name}",
                }
                for b in Booking.objects.filter(user=subscription.user)
            ]
            items.extend(bookings)

        # TODO: include events
        return items

    def item_title(self, item):
        return item["title"]

    def item_guid(self, item):
        return f"{item['id']}@d-sektionen.se"

    def item_description(self, item):
        return item["description"]

    def item_start_datetime(self, item):
        return item["start"]

    def item_end_datetime(self, item):
        return item["end"]

    def item_link(self, item):
        return ""

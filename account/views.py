from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import redirect
from django.conf import settings
from django_ical.views import ICalFeed
from django.utils.timezone import get_current_timezone
from rest_framework import mixins, viewsets, status, exceptions
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.decorators import list_route, action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from app.permissions import FixedDjangoModelPermissions
from booking.models import Booking


from .serializers import (
    MeSerializer,
    SimpleUserSerializer,
    InfomailUserSerializer,
    CalendarSubscriptionSerializer,
    ProfileSerializer,
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


class MeView(mixins.RetrieveModelMixin, GenericAPIView):
    serializer_class = MeSerializer
    queryset = User.objects.all()

    def get_object(self):
        return self.request.user

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class IdentificationTokenView(APIView):
    """
    Returns a jwt token, for identifying a user, NOT to be used for auth.

    Currently used to enable user identifying QR codes for the checkin app.
    (The QR codes are generated and read client side)

    """

    def get(self, request, *args, **kwargs):
        token = generate_id_token(request.user)
        return Response({"token": token}, status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        """
        Verify a token (returns a user)
        
        example input:
        ```
        {
            "token": "string"
        }
        ```
        """
        try:
            user = read_id_token(request.data["token"])
        except:
            raise exceptions.ParseError(detail="Token is invalid.")

        return Response(SimpleUserSerializer(user).data, status.HTTP_200_OK)


class InfomailSubscriberView(mixins.ListModelMixin, GenericAPIView):
    """
    Returns all users who are infomail subscribers.
    """

    permission_classes = [FixedDjangoModelPermissions]
    queryset = User.objects.filter(profile__infomail_subscriber=True)
    serializer_class = InfomailUserSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class ProfileView(mixins.UpdateModelMixin, mixins.RetrieveModelMixin, GenericAPIView):
    serializer_class = ProfileSerializer

    def get_object(self):
        return self.request.user.profile

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


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

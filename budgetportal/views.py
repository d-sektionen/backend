from django.shortcuts import render
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
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import action

from app.permissions import FixedDjangoModelPermissions
from .models import BudgetEntry
from .serializers import BudgetEntrySerializer, ArticleSerializer, ApprovalSerializer
from .permissions import BudgetEntryPermissions

# Create your views here.
class BudgetEntryViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows bookings to be viewed, created, edited or deleted.
    """

    queryset = BudgetEntry.objects.all()
    serializer_class = BudgetEntrySerializer
    permission_classes = (BudgetEntryPermissions,)

    def get_serializer_class(self):
        if self.action == 'approve':
            print("approve_serializer")
            return ApprovalSerializer
        return BudgetEntrySerializer

    def get_queryset(self):
        queryset = BudgetEntry.objects.all()
        article = self.request.query_params.get("articles", None)
        date = self.request.query_params.get("date", None)
        user = self.request.query_params.get("user", None)
        confirmed = self.request.query_params.get("confirmed", None)
        #restricted_timeslot = self.request.query_params.get("restricted_timeslot", None)

        if user == "me":
            user = self.request.user.id

#        if article:
#            queryset = queryset.filter(articles=article)
 #       if date != None:
#            queryset = queryset.filter(end__gt=timezone.now())
        if user:
            queryset = queryset.filter(user=user)
        if confirmed:
            queryset = queryset.filter(confirmed=confirmed)
       # if restricted_timeslot:
       #     queryset = queryset.filter(restricted_timeslot=restricted_timeslot)
        return queryset

    def perform_create(self, serializer):
        print("perform_create")
        auto_confirm = False
        data = serializer.validated_data
        #auto_confirm = self.should_auto_confirm(data)
        serializer.save()

    @action(detail=True, methods=['put'], permission_classes=[FixedDjangoModelPermissions]) 
    def approve(self, request, pk=None):

        keys = request.data.keys()
        if str(request.data['user_id']) != str(self.request.user.id):
            print("Different users")
            return Response(status=status.HTTP_403_FORBIDDEN, data="Different users")
        
        entry = self.get_object()

        if ('approvedKas' in keys):
            # Check if requesting user is a cashier for correct section
            print("committee",entry.committee)
            entry.approvedKas = bool(request.data["approvedKas"])
        else:
            entry.approvedKas = False

        if('approvedDeg' in keys):
            # Check if requesting user is a member of deg
            print("committee",entry.committee)
            entry.approvedDeg = bool(request.data["approvedDeg"])
        else:
            entry.approvedDeg = False

        if ('payed' in keys):
            # Check if requesting user is a member of deg
            print("committee",entry.committee)
            entry.payed = bool(request.data["payed"])
        else:
            entry.payed = False
        
        entry.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_update(self, serializer):
        old_obj = self.get_object()
        new_data = serializer.validated_data
        auto_confirm = old_obj.confirmed
        # if time was changed we need to recalculate auto approval
        if old_obj.start != new_data["start"] or old_obj.end != new_data["end"]:
            if old_obj.confirmed:
                # Recalculate confirmation
                auto_confirm = self.should_auto_confirm(new_data, exists=True)

        serializer.save(confirmed=auto_confirm)
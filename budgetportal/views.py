from xml.etree.ElementTree import Comment
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import redirect
from django.conf import settings
from django_ical.views import ICalFeed
from django.utils.timezone import get_current_timezone
from rest_framework import mixins, viewsets, status, exceptions
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import action
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser

from app.permissions import FixedDjangoModelPermissions
from .models import BudgetEntry, File
from .serializers import BudgetEntrySerializer,  ApprovalSerializer, CommentSerializer, FileSerializer
from .permissions import BudgetEntryPermissions
from committee.models import Committee


class FileViewSet(viewsets.ModelViewSet):
    serializer_class = FileSerializer
    permission_classes = (BudgetEntryPermissions,)
    queryset = File.objects.all()
    http_method_names = ['get']


class BudgetEntryViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows budget entries to be viewed, created, edited or deleted.
    """

    queryset = BudgetEntry.objects.all()
    serializer_class = BudgetEntrySerializer
    permission_classes = (BudgetEntryPermissions,)
    parser_classes = [FormParser, MultiPartParser]

    def get_serializer_class(self):
        if self.action == 'approve':
            return ApprovalSerializer
        if self.action == 'comment':
            return CommentSerializer
        return BudgetEntrySerializer

    def get_queryset(self):
        queryset = BudgetEntry.objects.all()
        date = self.request.query_params.get("date", None)
        user = self.request.query_params.get("user", None)
        approvedKas = self.request.query_params.get("approvedKas", None)
        approvedDeg = self.request.query_params.get("approvedDeg", None)
        payed = self.request.query_params.get("payed", None)

        """
        # check if user is privilged user that is allowed to view all entries
        # otherwise, filter so they only see their own
        if False:
            user = self.request.user.id
            queryset = BudgetEntry.objects.all()
            queryset = queryset.filter(user=user)
        """

        if date != None:
            queryset = queryset.filter(date__gt=date)
        if user:
            queryset = queryset.filter(user=user)
        if approvedKas:
            queryset = queryset.filter(approvedKas=approvedKas)
        if approvedDeg:
            queryset = queryset.filter(approvedDeg=approvedDeg)
        if payed:
            queryset = queryset.filter(payed=payed)

        # TODO: when deg committee has been entered into the database, change to proper name below
        # If user is in DEG, return all
        deg_committee = Committee.objects.filter(name='deg').first()
        if deg_committee and deg_committee.members.filter(id=self.request.user.id).exists():
            return queryset

        # Else only return user's own entries or ones associated
        # with the committees the user is a contact/cashier for
        query_filter = Q(user=self.request.user)
        for committee in self.request.user.contact_for.all():
            query_filter = query_filter | Q(committee__id=committee.id)
            
        return queryset.filter(query_filter)

    """
    def perform_create(self, serializer):
        obj = serializer.save()
        for f in self.request.data.getlist('files'):
            mf = MyFile.objects.create(file=f)
            obj.files.add(mf)
    """

    def perform_create(self, serializer):
        print(self.request.data)
        auto_confirm = False
        data = serializer.validated_data
        serializer.save()

        # TODO: send mail to DEG and treasurerer

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

    @action(detail=True, methods=['put'], permission_classes=[FixedDjangoModelPermissions]) 
    def approve(self, request: Request, pk=None):
        data_keys = request.data.keys()
        entry = self.get_object()
        
        # Check if the request user is the one specified
        if str(request.data['user_id']) != str(request.user.id):
            return Response('Different users', status.HTTP_403_FORBIDDEN)

        # TODO: when deg committee has been entered into the database, change to proper name below
        deg_committee = Committee.objects.filter(name='deg').first()
        is_in_deg = False
        if deg_committee:
            is_in_deg = deg_committee.members.filter(id=request.user.id).exists()

        # If approveDeg is sent, mark field if user is in deg
        if 'approvedDeg' in data_keys:
            if is_in_deg:
                entry.approvedDeg = bool(request.data['approvedDeg'])
                # TODO: send mail to user if denied
        else:
            entry.approvedDeg = False

        # If approveKas is sent, mark field if user is cashier of the entry committee
        if 'approvedKas' in data_keys:
            committee_cashier = Committee.objects.filter(name=entry.committee.name).first().contact
            if request.user == committee_cashier or is_in_deg:
                entry.approvedKas = bool(request.data['approvedKas'])
                # TODO: send mail to user if denied
        else:
            entry.approvedKas = False

        # If payed is sent, mark field if user is in deg
        if 'payed' in data_keys:
            if is_in_deg:
                entry.payed = bool(request.data['payed'])
                # TODO: send mail to user if payed
        else:
            entry.payed = False

        entry.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['put'], permission_classes=[FixedDjangoModelPermissions]) 
    def comment(self, request: Request, pk=None):
        data_keys = request.data.keys()
        
        # Check if the request user is the one specified
        if str(request.data['user_id']) != str(request.user.id):
            return Response('Different users', status.HTTP_403_FORBIDDEN)

        # TODO: check if user is allowed to comment (user in correct section)
        if False:
            return Response(status=status.HTTP_403_FORBIDDEN, data="Not allowed to comment")

        entry = self.get_object()        
        if True:
            if entry.comment:
                entry.comment += " " + str(request.data["comment"])
            else:
                entry.comment = str(request.data["comment"]) 
        
        entry.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

from xml.etree.ElementTree import Comment
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
from .serializers import BudgetEntrySerializer, ArticleSerializer, ApprovalSerializer, CommentSerializer
from .permissions import BudgetEntryPermissions
from committee.models import Committee

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
        if self.action == 'comment':
            print("comment")
            return CommentSerializer
        return BudgetEntrySerializer

    def get_queryset(self):
        queryset = BudgetEntry.objects.all()
        date = self.request.query_params.get("date", None)
        user = self.request.query_params.get("user", None)
        approvedKas = self.request.query_params.get("approvedKas", None)
        approvedDeg = self.request.query_params.get("approvedDeg", None)
        payed = self.request.query_params.get("payed", None)

        # check if user is privilged user that is allowed to view all entries
        # otherwise, filter so they only see their own
        if False:
            user = self.request.user.id
            queryset = BudgetEntry.objects.all()
            queryset = queryset.filter(user=user)

#       if date != None:
#            queryset = queryset.filter(end__gt=timezone.now())
        if user:
            queryset = queryset.filter(user=user)
        if approvedKas:
            queryset = queryset.filter(approvedKas=approvedKas)
        if approvedDeg:
            queryset = queryset.filter(approvedDeg=approvedDeg)
        if payed:
            queryset = queryset.filter(payed=payed)
        return queryset

    def perform_create(self, serializer):
        print("perform_create")
        auto_confirm = False
        data = serializer.validated_data
        #auto_confirm = self.should_auto_confirm(data)
        if self.request.method == 'POST':
            files = self.request.FILES.getlist('list_test')
            if files:
                print("list")
                self.request.data.pop('image2')
                
        serializer.save()

    @action(detail=True, methods=['put'], permission_classes=[FixedDjangoModelPermissions]) 
    def approve(self, request, pk=None):

        keys = request.data.keys()
        if str(request.data['user_id']) != str(self.request.user.id):
            print("Different users")
            return Response(status=status.HTTP_403_FORBIDDEN, data="Different users")
        
        entry = self.get_object()
        # Check if the user is part of deg
        committies = Committee.objects.all()
        degCommittee = Committee.objects.filter(name="deg")
        isDeg = False
        if degCommittee:
            isDeg = degCommittee.members.filter(username=self.request.user)

        if ('approvedKas' in keys):
            # Check if requesting user is a cashier for correct section
            committie_cashier = committies.filter(name=entry.committee.name).first().contact
            if self.request.user == committie_cashier or isDeg:
                entry.approvedKas = bool(request.data["approvedKas"])
        else:
            entry.approvedKas = False


        #print(Committee.objects.all())
        #print(entry.committee.contact)
        #print(entry.committee.members.filter(user=self.request.user))
        #print("...", Committee.objects.filter())
            
        if('approvedDeg' in keys):
            # Check if requesting user is a member of deg
            #TODO: Currently no way to check if a user is a deg member
            entry.committee.members.filter(username=self.request.user)
            if(True):
                entry.approvedDeg = bool(request.data["approvedDeg"])
        else:
            entry.approvedDeg = False

        if ('payed' in keys):
            # Check if requesting user is a member of deg
            #TODO: Currently no way to check if a user is a deg member
            if(True):
                entry.payed = bool(request.data["payed"])
        else:
            entry.payed = False
        
        entry.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['put'], permission_classes=[FixedDjangoModelPermissions]) 
    def comment(self, request, pk=None):
        keys = request.data.keys()
        if str(request.data['user_id']) != str(self.request.user.id):
            print("Different users")
            return Response(status=status.HTTP_403_FORBIDDEN, data="Different users")
        
        #Check if user is allowed to comment (user in correct section)
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
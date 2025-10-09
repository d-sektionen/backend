from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser

from . import email
from .models import BudgetEntry, File
from .serializers import (
    BudgetEntrySerializer,
    ApprovalSerializer,
    CommentSerializer,
    FileSerializer,
)
from .permissions import BudgetEntryPermissions

from ..app.permissions import FixedDjangoModelPermissions
from ..committee.models import Committee
from ..committee.utils import get_deg_committee


class FileViewSet(viewsets.ModelViewSet):
    serializer_class = FileSerializer
    permission_classes = (BudgetEntryPermissions,)
    queryset = File.objects.all()
    http_method_names = ["get"]


class BudgetEntryViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows budget entries to be viewed, created, edited or deleted.
    """

    queryset = BudgetEntry.objects.all()
    serializer_class = BudgetEntrySerializer
    permission_classes = (BudgetEntryPermissions,)
    parser_classes = [FormParser, MultiPartParser]

    def get_serializer_class(self):
        if self.action == "approve":
            return ApprovalSerializer
        if self.action == "comment":
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

        if date is not None:
            queryset = queryset.filter(date__gt=date)
        if user:
            queryset = queryset.filter(user__username=user)
        if approvedKas:
            queryset = queryset.filter(approvedKas=approvedKas)
        if approvedDeg:
            queryset = queryset.filter(approvedDeg=approvedDeg)
        if payed:
            queryset = queryset.filter(payed=payed)

        # If user is in DEG, return all
        deg_committee = get_deg_committee()
        if deg_committee.members.filter(id=self.request.user.id).exists():
            return queryset

        # Else only return user's own entries or ones associated
        # with the committees the user is a contact/cashier for
        query_filter = Q(user=self.request.user)
        for committee in self.request.user.treasurer_for.all():
            query_filter = query_filter | Q(committee__id=committee.id)

        return queryset.filter(query_filter)

    def perform_create(self, serializer):
        instance = serializer.save()
        email.send_new_entry_mails(self.request.user, instance)

    def perform_update(self, serializer):
        # print(f"{self.request.data = }")
        # Maybe needs to be re-approved?
        serializer.save()

    @action(
        detail=True, methods=["put"], permission_classes=[FixedDjangoModelPermissions]
    )
    def approve(self, request: Request, pk=None):
        data_keys = request.data.keys()
        entry = self.get_object()

        if entry.denied:
            return Response("Entry is denied", status.HTTP_403_FORBIDDEN)

        deg_committee = get_deg_committee()
        is_in_deg = deg_committee.members.filter(id=request.user.id).exists()

        # TODO: change to check if user is section cashier
        is_section_cashier = True

        # If approveKas is sent, mark field if user is cashier of the entry committee
        if "approvedKas" in data_keys:
            committee_cashier = (
                Committee.objects.filter(name=entry.committee.name).first().treasurer
            )
            print("committee cashier", committee_cashier)
            if (
                request.user == committee_cashier or is_in_deg or is_section_cashier
            ):  # TODO: should is_in_deg be here
                entry.approvedKas = bool(request.data["approvedKas"])
        else:
            entry.approvedKas = False

        # If approveDeg is sent, mark field if user is in deg
        if "approvedDeg" in data_keys:
            if is_in_deg or is_section_cashier:
                approvedDegChanged = (
                    bool(request.data["approvedDeg"]) != entry.approvedDeg
                )
                entry.approvedDeg = bool(request.data["approvedDeg"])
                if entry.approvedDeg and approvedDegChanged:
                    email.send_unpayed_entries_mail(entry)
        else:
            entry.approvedDeg = False

        # If payed is sent, mark field if user is section cashier
        if "payed" in data_keys:
            if is_section_cashier:
                entry.payed = bool(request.data["payed"])
                if entry.payed:
                    email.send_entry_payed_mail(request.user, entry)
        else:
            entry.payed = False

        # If denied is sent, mark field if user is section cashier
        if "denied" in data_keys:
            committee_cashier = (
                Committee.objects.filter(name=entry.committee.name).first().treasurer
            )
            print("committee cashier", committee_cashier)
            if (
                request.user == committee_cashier or is_in_deg or is_section_cashier
            ):  # TODO: should is_in_deg be here
                entry.denied = bool(request.data["denied"])
                if entry.denied:
                    email.send_entry_denied_mail(request.user, entry)
        else:
            entry.denied = False

        entry.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True, methods=["put"], permission_classes=[FixedDjangoModelPermissions]
    )
    def comment(self, request: Request, pk=None):
        entry = self.get_object()

        # TODO: check if user is allowed to comment (user in correct section)
        if False:
            return Response(
                status=status.HTTP_403_FORBIDDEN, data="Not allowed to comment"
            )
        elif entry.comment:
            print("test")
            entry.comment += " " + str(request.data["comment"])
        else:
            entry.comment = str(request.data["comment"])
        entry.save()
        print(entry.comment)
        return Response(status=status.HTTP_200_OK)

from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser

from . import email
from .models import BudgetEntry, File
from .serializers import BudgetEntrySerializer,  ApprovalSerializer, CommentSerializer, FileSerializer
from .permissions import BudgetEntryPermissions

from app.permissions import FixedDjangoModelPermissions
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
            queryset = queryset.filter(user__username=user)
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

    def perform_create(self, serializer):
        instance = serializer.save()

        # Send e-mail to entry's committee's treasurer
        treasurer_body = f"Hej!\n{self.request.user.get_full_name()} har fyllt ut ett nytt personligt utlägg som gäller ditt utskott. Gå in och granska det här: [länk]"  # TODO: fill in link
        email.send(
            "TREASURER TEST", # TODO: change
            treasurer_body,
            instance.committee.contact.email,
        )

        # Send second e-mail to entry's committee's treasurer
        unpayed_entry_count = BudgetEntry.objects.filter(payed=False, committee__contact=instance.committee.contact).count()
        treasurer_body_2 = f"Hej! Det finns {unpayed_entry_count} nya bokförda personliga utlägg för dig att betala ut. Du kommer åt dem här: [länk]"  # TODO: fill in link
        email.send(
            "TREASURER TEST 2", # TODO: change
            treasurer_body_2,
            instance.committee.contact.email,
        )

        # TODO: when deg committee has been entered into the database, change to proper name below
        # Send e-mail to DEG
        deg_committee = Committee.objects.filter(name='deg').first()
        if deg_committee:
            deg_body = f"Hej!\nDet finns ett nytt personligt utlägg för {instance.committee.name} för dig att granska och bokföra, du hittar utlägget här: [länk]"  # TODO: fill in link
            email.send(
                "DEG TEST", # TODO: change
                deg_body,
                deg_committee.contact.email  # TODO: should be sent to all members?,
            )

    def perform_update(self, serializer):
        print(f'{self.request.data = }')
        # Maybe needs to be re-approved?
        serializer.save()

    @action(detail=True, methods=['put'], permission_classes=[FixedDjangoModelPermissions]) 
    def approve(self, request: Request, pk=None):
        data_keys = request.data.keys()
        entry = self.get_object()
        
        # Check if the request user is the one specified
        # TODO: dont think this is necessary
        #if str(request.data['user_id']) != str(request.user.id):
        #    return Response('Different users', status.HTTP_403_FORBIDDEN)

        # TODO: when deg committee has been entered into the database, change to proper name below
        deg_committee = Committee.objects.filter(name='deg').first()
        is_in_deg = False
        if deg_committee:
            is_in_deg = deg_committee.members.filter(id=request.user.id).exists()

        #Change to check if user is section cashier
        is_section_cashier = True

        # If approveDeg is sent, mark field if user is in deg
        if 'approvedDeg' in data_keys:
            if is_in_deg or is_section_cashier:
                entry.approvedDeg = bool(request.data['approvedDeg'])

                # Send mail to user if denied
                # TODO: make sure this is correct
                if not entry.approvedDeg:
                    email_body = f"Hej!\nDitt personliga utlägg för {entry.committee.name} har nekats med med motiveringen: [motivering]. Logga in på ditt konto på budgetportalen för att redigera ditt personliga utlägg och skicka in det igen."
                    email.send(
                        "DENIED BY DEG TEST", # TODO: change
                        email_body,
                        entry.user.email,
                    )
        else:
            entry.approvedDeg = False

        # If approveKas is sent, mark field if user is cashier of the entry committee
        if 'approvedKas' in data_keys:
            committee_cashier = Committee.objects.filter(name=entry.committee.name).first().contact
            print("committee cashier", committee_cashier)
            if request.user == committee_cashier or is_in_deg: # TODO: should is_in_deg be here
                entry.approvedKas = bool(request.data['approvedKas'])

                # Send mail to user if denied
                # TODO: make sure this is correct
                if not entry.approvedKas:
                    email_body = f"Hej!\nDitt personliga utlägg för {entry.committee.name} har nekats med med motiveringen: [motivering]. Logga in på ditt konto på budgetportalen för att redigera ditt personliga utlägg och skicka in det igen."
                    email.send(
                        "DENIED BY TREASURER TEST", # TODO: change
                        email_body,
                        entry.user.email,
                    )
        else:
            entry.approvedKas = False

        # If payed is sent, mark field if user is in deg
        if 'payed' in data_keys:
            if is_in_deg or is_section_cashier:
                entry.payed = bool(request.data['payed'])

                # Send mail to user if payed
                if entry.payed:
                    email_body = f"Hej!\nDitt personliga utlägg för {entry.committee.name} har betalats ut av {request.user.get_full_name()}, pengarna bör finnas på ditt konto inom 1-2 bankdagar."
                    email.send(
                        "PAYED TEST", # TODO: change
                        email_body,
                        entry.user.email,
                    )
        else:
            entry.payed = False

        entry.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['put'], permission_classes=[FixedDjangoModelPermissions]) 
    def comment(self, request: Request, pk=None):
        entry = self.get_object()
        
        # Check if the request user is the one specified
        if str(request.data['user_id']) != str(request.user.id):
            return Response('Different users', status.HTTP_403_FORBIDDEN)

        # TODO: check if user is allowed to comment (user in correct section)
        if False:
            return Response(status=status.HTTP_403_FORBIDDEN, data="Not allowed to comment")
        elif entry.comment:
            entry.comment += " " + str(request.data["comment"])
        else:
            entry.comment = str(request.data["comment"]) 

        entry.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

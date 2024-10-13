from django.template.loader import get_template
from rest_framework.decorators import (
    action,
)
from rest_framework import viewsets
from rest_framework.response import Response
from account.permissions import AllowMembers
from rest_framework import status

from infomail.serializers import InfomailSerializer


class InfoMailViewSet(viewsets.ViewSet):
    # TODO: Add proper perms
    permission_classes = (AllowMembers,)

    def list(self, request):
        return Response({})

    @action(
        detail=False,
        methods=["post"],
    )
    def preview(self, request):
        serializer = InfomailSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

        subject_template = get_template("email/infomail.subject.txt")
        content_template = get_template("email/infomail.html")

        subject_html = subject_template.render(
            {"subject": serializer.validated_data["subject"]}
        )
        content_html = content_template.render(
            {"content": serializer.validated_data["content"]}
        )

        return Response(
            {"subject": subject_html, "content": content_html},
        )

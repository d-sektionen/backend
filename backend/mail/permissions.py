from rest_framework import permissions
from ..account.models import Profile


class SenderPermission(permissions.BasePermission):
    """
    Custom permission to only allow infomail senders to send mails.
    """

    def has_object_permission(self, request, view, obj) -> bool:
        profile = Profile.objects.get(user=request.user)

        return profile.infomail_sender

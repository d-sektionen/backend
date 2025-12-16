from rest_framework import permissions
from ..account.models import Profile


class SenderPermission(permissions.BasePermission):
    """
    Custom permission to only allow infomail senders to send mails.
    """

    def has_object_permission(self, request, view, obj) -> bool:
        return self.has_permission(request, view)

    def has_permission(self, request, view) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False
        try:
            profile = Profile.objects.get(user=request.user)
            return profile.infomail_sender
        except Profile.DoesNotExist:
            return False

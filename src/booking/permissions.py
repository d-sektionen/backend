from rest_framework import permissions
from membership.utils import check_membership
from .models import Blacklisted
from datetime import datetime


class BookingPermissions(permissions.BasePermission):
    """
  Custom permission for a booking.
  """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Create only allowed if section member
        if request.method == "POST" and not (
            request.user.has_perm("booking.add_booking")
            or check_membership(request.user.username)
        ):
            return False

        if (
            request.method == "POST"
            and Blacklisted.objects.filter(
                user=request.user, expires__gt=datetime.now()
            ).exists()
        ):
            return False

        return True

    def has_object_permission(self, request, view, obj):
        if not request.user:
            return False

        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Allow delete if admin
        if request.method == "DELETE" and request.user.has_perm(
            "booking.delete_booking"
        ):
            return True

        # Write permissions are only allowed to the owner of the booking.
        return obj.user == request.user

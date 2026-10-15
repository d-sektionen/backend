from rest_framework import permissions

from ..membership.utils import check_membership


class CommitteePermissions(permissions.BasePermission):
    """
    Custom permission for a booking.
    """

    def has_permission(self, request, view):
        if (
            not request.user
            or not request.user.is_authenticated
            or not request.user.has_perm("committee.add_committee")
        ):
            return False

        # Create only allowed if section member
        if request.method == "POST" and not check_membership(request.user.username):
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
        if request.method == "POST" and request.user.has_perm(
            "committee.committee.change_committee"
        ):
            return True
        print("can modify")
        # Write permissions are only allowed to the owner of the booking.
        return obj.user == request.user

from rest_framework import permissions

from membership.utils import check_membership


class BudgetEntryPermissions(permissions.BasePermission):
    """
    Custom permission for a budget entry.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Create only allowed if section member
        if request.method == "POST" and not (
            request.user.has_perm("budgetportal.add_budgetentry")
            or check_membership(request.user.username)
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
            "budgetportal.delete_budgetentry"
        ):
            return True

        # Write permissions are only allowed to the owner of the booking.
        return obj.user == request.user

from rest_framework import permissions

# NOTE: Copied from src/booking/permissions.py and modified to fit the email functionality
class EmailPermission(permissions.BasePermission):
    """
    Custom permission for an email.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Create only allowed if section member
        if request.method == "POST" and not (
            request.user.has_perm("email.add_email")
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
            "email.delete_email"
        ):
            return True

        # Write permissions are only allowed to the owner of the email.
        return obj.user == request.user
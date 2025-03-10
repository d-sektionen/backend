from rest_framework import permissions


class PhotoPermissions(permissions.BasePermission):
    """
    Custom permission for a photo.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Create only allowed if section member
        if request.method == "POST" and not request.user.has_perm("photo.add_photo"):
            return False

        return True

    def has_object_permission(self, request, view, obj):
        if not request.user:
            return False

        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Allow delete if appropriate perm
        if request.method == "DELETE" and request.user.has_perm("photo.delete_photo"):
            return True

        # Write permissions are only allowed to the owner of the photo.
        return obj.user == request.user

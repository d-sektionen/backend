from rest_framework import permissions
from membership.utils import check_membership


class LoggingPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        return True

    def has_object_permission(self, request, view, obj):
        if request.user.id is not obj.user.id:
            return False
        
        return True
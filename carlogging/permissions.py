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


class LoggingAdminPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == 'GET':
            return request.user.has_perms((
                'booking.add_booking',
                'booking.change_booking',
                'booking.delete_booking',
                'booking.view_booking'
            ))  # and not request.user.has_perms(("booking.add_booking"))  # for debug
        return False

    def has_object_permission(self, request, view, obj):
        return False

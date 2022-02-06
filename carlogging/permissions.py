from rest_framework import permissions
from rest_framework.request import Request

from membership.utils import check_membership


class LoggingPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return request.user.id is obj.user.id


class LoggingAdminPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == 'GET':
            return request.user.has_perms(('booking.add_booking',
                                           'booking.change_booking',
                                           'booking.delete_booking',
                                           'booking.view_booking'))
        return False

    def has_object_permission(self, request, view, obj):
        return False

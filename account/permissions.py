from rest_framework.permissions import BasePermission
from membership.utils import check_membership, check_alumnimembership


class IsUser(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_authenticated:
            return obj == request.user
        else:
            return False


class AllowMembers(BasePermission):
    def has_permission(self, request, view):
        if request.user:
            return check_membership(request.user.username)
        else:
            return False


class AllowMembersAndAlumnis(BasePermission):
    def has_permission(self, request, view):
        if request.user:
            return check_membership(request.user.username) or check_alumnimembership(request.user.username)
        else:
            return False
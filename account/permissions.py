from rest_framework.permissions import BasePermission
from membership.utils import check_membership

class IsUser(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user:
            return obj == request.user
        else:
            return False

class AllowSectionMembers(BasePermission):
    def has_permission(self, request, view):
        if request.user:
            return check_membership(request.user.username)
        else:
            return False

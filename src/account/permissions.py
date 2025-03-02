from rest_framework.permissions import BasePermission
from account.models import Profile
from membership.utils import check_membership


class IsCommitteeActive(BasePermission):
    def has_object_permission(self, request, view, obj):
        profile = Profile.objects.get(user=request.user)

        return profile.has_active_committee_membership()


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

from rest_framework.permissions import BasePermission


from membership.utils import check_membership
from app.permissions import RestPermission
from .models import Meeting


class OpenAttendancePermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user:
            return False
        return check_membership(request.user.get_username())

    def has_object_permission(self, request, view, obj):
        if not request.user:
            return False
        return obj.meeting.open_attendance


class VotePermission(RestPermission):
    def has_action_permission(self, request, view, action):
        if action == "CREATE":
            return request.user.has_perm("voting.add_vote")
        return True

    def has_object_permission(self, request, view, obj):
        # Could be split up to different methods
        return request.user.has_perms(["voting.change_vote", "voting.view_vote"])

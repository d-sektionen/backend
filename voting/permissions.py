from rest_framework.permissions import BasePermission


from membership.utils import check_membership
from app.permissions import RestPermission
from .models import Meeting


class SpeakerRequestPermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.method == "POST":
            if not check_membership(request.user.get_username()):
                return False

        return True


class OpenAttendancePermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user:
            return False
        return check_membership(request.user.get_username())

    def has_object_permission(self, request, view, obj):
        if not request.user:
            return False
        return obj.meeting.open_attendance

from rest_framework.permissions import BasePermission


from membership.utils import check_membership
from .models import Meeting
from django.db.models import Q


class SpeakerRequestPermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.method == "POST":
            if not check_membership(request.user.get_username()):
                in_a_meeting = Meeting.objects.filter(archived=False).filter(Q(attendants__user=request.user))
                if in_a_meeting:
                    return True

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

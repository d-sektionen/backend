from rest_framework.permissions import BasePermission

from voting.models import Scanner


class AdminMeetingPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.meeting.section.is_admin(request.user)


class ScannerOrAdminMeetingPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method == "POST" or request.method == "DELETE":
            is_scanner_for_meeting = Scanner.objects.filter(user=request.user, meeting=obj.meeting).exists()
            return is_scanner_for_meeting or obj.meeting.section.is_admin(request.user)
        else:
            return obj.meeting.section.is_admin(request.user)


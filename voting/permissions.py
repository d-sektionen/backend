from rest_framework.permissions import BasePermission

from account.models import Section
from app.permissions import RestPermission
from voting.models import Scanner, Meeting


class ScannerPermission(RestPermission):
    def has_action_permission(self, request, view, action):
        if action == 'LIST' or action == 'CREATE' or (action == 'DESTROY' and 'pk' not in view.kwargs):
            meeting = self.get_foreign_object(request, Meeting, 'meeting')
            if meeting is not None:
                return meeting.section.is_admin(request.user)
            else:
                # Sending in no meeting should allow scanners to retrieve "them selves"
                return True

        return True

    def has_object_permission(self, request, view, obj):
        return obj.meeting.section.is_admin(request.user)


class AttendantPermission(RestPermission):
    def has_action_permission(self, request, view, action):
        if action == 'LIST':
            meeting = self.get_foreign_object(request, Meeting, 'meeting')
            if meeting is not None:
                return meeting.section.is_admin(request.user)
            else:
                return False
        elif action == 'CREATE' or (action == 'DESTROY' and 'pk' not in view.kwargs):
            meeting = self.get_foreign_object(request, Meeting, 'meeting')
            if meeting is not None:
                return meeting.section.is_admin(request.user) or Scanner.objects.filter(user=request.user, meeting=meeting).exists()

        return True

    def has_object_permission(self, request, view, obj):
        return obj.meeting.section.is_admin(request.user)


class VotePermission(RestPermission):
    def has_action_permission(self, request, view, action):
        if action == 'CREATE':
            meeting = self.get_foreign_object(request, Meeting, 'meeting')
            if meeting is not None:
                return meeting.section.is_admin(request.user)
            else:
                return False
        else:
            return True

    def has_object_permission(self, request, view, obj):
        return obj.meeting.section.is_admin(request.user)


class AdminSectionPermission(RestPermission):
    def has_action_permission(self, request, view, action):
        if action == 'CREATE':
            section = self.get_foreign_object(request, Section, 'section')
            if section is not None:
                return section.is_admin(request.user)
            else:
                return False

        return True

    def has_object_permission(self, request, view, obj):
        return obj.section.is_admin(request.user)


class ScannerOrAdminMeetingPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method == "POST" or request.method == "DELETE":
            is_scanner_for_meeting = Scanner.objects.filter(user=request.user, meeting=obj.meeting).exists()
            return is_scanner_for_meeting or obj.meeting.section.is_admin(request.user)
        else:
            return obj.meeting.section.is_admin(request.user)


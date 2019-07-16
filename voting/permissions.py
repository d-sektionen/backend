from app.permissions import RestPermission
from .models import Meeting


# class AttendantPermission(RestPermission):
#     def has_action_permission(self, request, view, action):
#         if action == 'LIST':
#             return request.user.has_perm('voting.view_attendant')
        
#         delete_all = action == 'DESTROY' and 'pk' not in view.kwargs
#         if action == 'CREATE' or delete_all:
#             meeting = self.get_foreign_object(request, Meeting, 'meeting')
#             if meeting is not None:
#                 return request.user.has_perms(['voting.delete_attendant', 'voting.add_attendant']) or Scanner.objects.filter(user=request.user, meeting=meeting).exists()

#         return True

#     def has_object_permission(self, request, view, obj):
#         return request.user.has_perm('voting.delete_attendant')


class VotePermission(RestPermission):
    def has_action_permission(self, request, view, action):
        if action == 'CREATE':
            return request.user.has_perm('voting.add_vote')
        return True

    def has_object_permission(self, request, view, obj):
        # Could be split up to different methods
        return request.user.has_perms(['voting.change_vote', 'voting.view_vote'])


# class AdminSectionPermission(RestPermission):
#     def has_action_permission(self, request, view, action):
#         if action == 'CREATE':
#             section = self.get_foreign_object(request, Section, 'section')
#             if section is not None:
#                 return section.is_admin(request.user) # TODO: change admin identification
#             else:
#                 return False

#         return True

#     def has_object_permission(self, request, view, obj):
#         return obj.section.is_admin(request.user) # TODO: change admin identification
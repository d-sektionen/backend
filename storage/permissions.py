from django.contrib.auth.models import Group

from account.models import is_user_in_group
from app.permissions import RestPermission
from storage.models import Location


class BookingPermission(RestPermission):
    def has_action_permission(self, request, view, action):
        if action == 'CREATE':
            group = self.get_foreign_object(request, Group, 'group')
            if group is not None:
                return is_user_in_group(group, request.user)

        return True

    def has_object_permission(self, request, view, obj):
        if request.method == 'GET':
            # Anyone can view a booking
            return True
        else:
            return obj.has_permissions(request.user)


class ObjectPermission(RestPermission):
    def has_action_permission(self, request, view, action):
        if action == 'CREATE':
            location = self.get_foreign_object(request, Location, 'location')
            if location is not None:
                print(location.has_permissions(request.user))
                return location.has_permissions(request.user)

        return True

    def has_object_permission(self, request, view, obj):
        return obj.has_permissions(request.user)

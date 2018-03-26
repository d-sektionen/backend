from rest_framework import permissions


class BookingPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        # TODO: Verify that the user is a member of the supplied group
        print(request)
        return True

    def has_object_permission(self, request, view, obj):
        if request.method == 'GET':
            # Anyone can view a booking
            return True
        else:
            return obj.has_permissions(request.user)


class ObjectPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        # TODO: Verify that the user has permission to create the object in its location room
        return True

    def has_object_permission(self, request, view, obj):
        return obj.has_permissions(request.user)

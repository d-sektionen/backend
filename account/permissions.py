from rest_framework.permissions import BasePermission

class IsUser(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user:
            return obj == request.user
        else:
            return False
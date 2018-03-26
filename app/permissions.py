from rest_framework.permissions import IsAuthenticated, BasePermission


class AllowOptionsAuthentication(IsAuthenticated):
    def has_permission(self, request, view):
        if request.method == 'OPTIONS':
            return True
        return request.user and request.user.is_authenticated


class RestPermission(BasePermission):
    def has_permission(self, request, view):
        return self.has_action_permission(request, view, self.get_action(request, view))

    def has_object_permission(self, request, view, obj):
        return self.has_action_object_permission(request, view, obj, self.get_action(request, view))

    def has_action_permission(self, request, view, action):
        return True

    def has_action_object_permission(self, request, view, obj, action):
        return True

    def get_action(self, request, view):
        method = request.method
        if method == 'GET':
            if 'pk' in view.kwargs:
                return 'RETRIEVE'
            else:
                return 'LIST'
        elif method == 'POST':
            return 'CREATE'
        elif method == 'DELETE':
            return 'DESTROY'
        else:
            return 'UPDATE'

    def get_foreign_object(self, request, model, key):
        try:
            pk = request.data.get(key)
            if pk is None:
                pk = request.query_params.get(key)

            if pk is not None:
                return model.objects.get(pk=pk)
        except model.DoesNotExist:
            pass

        return None

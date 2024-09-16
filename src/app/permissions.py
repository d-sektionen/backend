from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions


class AllowOptionsAuthentication(IsAuthenticated):
    def has_permission(self, request, view):
        if request.method == "OPTIONS":
            return True
        return request.user and request.user.is_authenticated


class FixedDjangoModelPermissions(DjangoModelPermissions):
    """
    DjangoModelPermissions does not handle view permissions from django 2.1,
    this fixes that.
    """

    def __init__(self):
        self.perms_map["GET"] = ["%(app_label)s.view_%(model_name)s"]

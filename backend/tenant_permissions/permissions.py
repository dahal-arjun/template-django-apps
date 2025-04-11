from rest_framework.permissions import BasePermission
from tenant_permissions.models import Role, UserRoles, UserPermissions


class HasRole(BasePermission):
    def __init__(self, roles):
        if isinstance(roles, str):
            self.roles = [roles]
        else:
            self.roles = roles

    def __call__(self):
        return self

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False


        return UserRoles.objects.filter(
            user=request.user,
            roles__name__in=self.roles
        ).exists()


class HasPermission(BasePermission):
    def __init__(self, permissions):
        if isinstance(permissions, str):
            self.permissions = [permissions]
        else:
            self.permissions = permissions

    def __call__(self):
        return self

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        return UserPermissions.objects.filter(
            user=request.user,
            permissions__name__in=self.permissions
        ).exists()

from rest_framework.permissions import BasePermission
from django.contrib.auth.models import (
    Group,
    Permission
)

class IsTenantMember(BasePermission):
    def has_permission(self, request, view):
        user = request.user

        if not user.is_authenticated:
            return False

        tenant = request.tenant

        if tenant is None:
            return False

        if tenant not in user.tenant.all():
            return False

        return True

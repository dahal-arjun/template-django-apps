from django.contrib.auth.models import Permission

from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from tenant_permissions.models import Role, User, UserRoles, UserPermissions
from tenant_permissions.serializers import (
    RoleSerializer,
    UserRolesSerializer,
    UserPermissionsSerializer,
    PermissionSerializer,
    MeSerializer
)

from rest_framework import generics
from django.db.models import Q

from tenant_permissions.permissions import HasRole


class PermissionsListAPIView(generics.ListAPIView):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer

    def get_queryset(self):
        exclude_range = list(range(1, 11)) + list(range(22, 28))
        queryset = self.queryset.exclude(content_type_id__in=exclude_range).order_by('content_type')
        return queryset


class RoleListCreateAPIView(generics.ListCreateAPIView):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [HasRole(["TENANT_ADMIN"]),]


class UserRolesListCreateAPIView(generics.ListCreateAPIView):
    queryset = UserRoles.objects.all()
    serializer_class = UserRolesSerializer
    permission_classes = [HasRole(["TENANT_ADMIN"]),]



class UserPermissionsListCreateAPIView(generics.ListCreateAPIView):
    queryset = UserPermissions.objects.all()
    serializer_class = UserPermissionsSerializer
    permission_classes = [HasRole(["TENANT_ADMIN"]),]


class Me(generics.GenericAPIView):
    serializer_class = MeSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"tenant": self.request.tenant})
        return context


    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

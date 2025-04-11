from django.urls import path, include
from rest_framework.routers import DefaultRouter
from tenant_permissions.views import (
    RoleListCreateAPIView,
    UserRolesListCreateAPIView,
    UserPermissionsListCreateAPIView,
    PermissionsListAPIView,
    Me
)


urlpatterns = [
    path('',PermissionsListAPIView.as_view(), name='permissions-list'),
    path('roles/', RoleListCreateAPIView.as_view(), name='role-list-create'),
    path('user-roles/', UserRolesListCreateAPIView.as_view(), name='user-role-create-list'),
    path('user-permissions/', UserPermissionsListCreateAPIView.as_view(), name='user-permissions-list-create'),
    path('me/', Me.as_view(),name='me')
]

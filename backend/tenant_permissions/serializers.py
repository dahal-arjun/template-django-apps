# serializers.py
from authentication.models import User
from rest_framework import serializers
from tenants.serializers import TenantSerializer
from django.contrib.auth.models import Permission
from tenant_permissions.models import UserRoles, Role, UserPermissions
from drf_spectacular.utils import extend_schema_field


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = '__all__'


class RoleSerializer(serializers.ModelSerializer):
    permission_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Permission.objects.all(), write_only=True
    )
    permissions = PermissionSerializer(many=True, read_only=True)

    class Meta:
        model = Role
        fields = ['id', 'name', 'permissions', 'created_at', 'permission_ids']

    def create(self, validated_data):
        permissions_data = validated_data.pop('permission_ids', [])
        role, created = Role.objects.get_or_create(**validated_data)

        permissions = Permission.objects.filter(id__in=permissions_data)
        role.permissions.set(permissions)
        return role

    def update(self, instance, validated_data):
        permissions_data = validated_data.pop('permission_ids', None)
        instance.name = validated_data.get('name', instance.name)
        instance.save()

        if permissions_data is not None:
            permissions = Permission.objects.filter(id__in=permissions_data)
            instance.permissions.set(permissions)
        return instance

class UserRolesSerializer(serializers.ModelSerializer):
    role_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Role.objects.all(), write_only=True
    )
    roles = RoleSerializer(many=True, read_only=True)

    class Meta:
        model = UserRoles
        fields = ['id', 'user', 'roles', 'role_ids']

    def create(self, validated_data):
        roles_data = validated_data.pop('role_ids', [])
        user_roles, created = UserRoles.objects.get_or_create(user=validated_data['user'])
        user_roles.roles.set(roles_data)
        return user_roles

    def update(self, instance, validated_data):
        roles_data = validated_data.pop('role_ids', None)
        if roles_data is not None:
            instance.roles.set(roles_data)
        return instance


class UserPermissionsSerializer(serializers.ModelSerializer):
    permission_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Permission.objects.all(), write_only=True
    )
    permissions = PermissionSerializer(many=True, read_only=True)

    class Meta:
        model = UserPermissions
        fields = ['id', 'user', 'permissions', 'permission_ids']

    def create(self, validated_data):
        permissions_data = validated_data.pop('permission_ids', [])
        user_permissions, created = UserPermissions.objects.get_or_create(user=validated_data['user'])
        user_permissions.permissions.set(permissions_data)
        return user_permissions

    def update(self, instance, validated_data):
        permissions_data = validated_data.pop('permission_ids', None)
        if permissions_data is not None:
            instance.permissions.set(permissions_data)
        return instance


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = (
            'password',
            'is_active',
            'is_verified',
            'is_staff',
            'is_superuser',
            'tenant',
            'groups',
            'user_permissions'
        )



class MeSerializer(serializers.Serializer):
    roles = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()

    @extend_schema_field(serializers.ListField(child=RoleSerializer()))
    def get_roles(self, instance):
        user_roles = UserRoles.objects.prefetch_related('roles').filter(user=instance).first()
        if user_roles:
            return RoleSerializer(user_roles.roles.all(), many=True).data
        return []

    @extend_schema_field(serializers.ListField(child=PermissionSerializer()))
    def get_permissions(self, instance):
        user_permissions = UserPermissions.objects.prefetch_related('permissions').filter(user=instance).first()
        if user_permissions:
            return PermissionSerializer(user_permissions.permissions.all(), many=True).data
        return []

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        # Add roles and permissions to the representation
        representation['roles'] = self.get_roles(instance)
        representation['permissions'] = self.get_permissions(instance)
        representation['tenant'] = TenantSerializer(self.context.get('tenant')).data
        representation['user'] = UserSerializer(instance).data

        return representation

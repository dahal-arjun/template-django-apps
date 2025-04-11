from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)

from django.db import models, transaction
from rest_framework_simplejwt.tokens import RefreshToken
import uuid
from django_tenants.utils import schema_context




class UserManager(BaseUserManager):

    def check_user_with_email_exist(self, email):
        return self.model.objects.filter(email=email).exists()

    @transaction.atomic
    def create_user(self, email, first_name, last_name, middle_name=None, password=None):
        if self.model.objects.filter(email=email).exists():
            raise TypeError('Account already exist')
        if email is None:
            raise TypeError('Users should have a Email')
        user = self.model(email=self.normalize_email(email))
        user.first_name = first_name
        user.last_name = last_name
        user.middle_name = middle_name

        user.set_password(password)
        user.save()
        return user

    @transaction.atomic
    def create_superuser(self, email, first_name, last_name, middle_name=None, password=None):
        if password is None:
            raise ValueError('Password should not be none')
        user = self.create_user(email, first_name, last_name, middle_name=None, password=None)
        user.is_superuser = True
        user.is_staff = True
        user.save()
        return user


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(max_length=255, unique=True, db_index=True)
    first_name = models.CharField(max_length=255)
    middle_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tenant = models.ManyToManyField('tenants.Tenant')

    USERNAME_FIELD = 'email'

    objects = UserManager()

    def __str__(self):
        return self.email

    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }

    def has_tenant_role(self, tenant_schema, role_name):
        with schema_context(tenant_schema):
            return self.user_roles.filter(roles__name=role_name).exists()

    def has_tenant_permission(self, tenant_schema, permission_codename):
        with schema_context(tenant_schema):
            return (
                self.user_roles.filter(roles__permissions__codename=permission_codename).exists() or
                self.user_permissions.filter(permissions__codename=permission_codename).exists()
            )

# models.py
from django.db import models
from django.contrib.auth.models import  Permission
from authentication.models import User

class Role(models.Model):
    name = models.CharField(unique=True, max_length=255)
    permissions = models.ManyToManyField(Permission, related_name='role_permissions')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['id']

class UserRoles(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    roles = models.ManyToManyField(Role, related_name='user_roles')

class UserPermissions(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    permissions = models.ManyToManyField(Permission, related_name='user_permissions')

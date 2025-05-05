from datetime import date

from django.db import models, transaction
from django_tenants.models import TenantMixin, DomainMixin
from django.utils import timezone
import random
import uuid

from authentication.models import User


class StatusChoices(models.TextChoices):
    ACTIVE = 'active', 'Active'
    INACTIVE = 'inactive', 'Inactive'
    SUSPENDED = 'suspended', 'Suspended'

class Tenant(TenantMixin):
    name = models.CharField(max_length=100, unique=True)
    admin_email = models.EmailField()
    # logo = models.FileField(upload_to='logos/', null=True, blank=True)
    tenant_status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.ACTIVE
    )
    settings = models.JSONField(blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True)

    auto_create_schema = True

    def is_subscription_active(self):
        return self.paid_until >= date.today()

    class Meta:
        permissions = [
            ('can_change_tenant_info', 'Can change tenant information'),
        ]



class Domain(DomainMixin):
    pass




class InvitationError(Exception):
    pass

class InvitationAlreadyAcceptedError(InvitationError):
    pass

class InvitationNotFoundError(InvitationError):
    pass

class InvitationTokenMismatchError(InvitationError):
    pass


class InvitationManager(models.Manager):
    def generate_token(self) -> str:
        return str(random.randint(100000, 999999))

    @transaction.atomic
    def create_invitation(self, email, tenant):
        if email  is None:
            raise TypeError('Email is required')
        if tenant is None:
            raise TypeError('Tenant is required')

        token = self.generate_token()
        invitation = Invitation.custom_manager.create(
            email=email,
            tenant=tenant,
            token=token
        )
        return invitation


    @transaction.atomic
    def accept_invitation(self, token):
        try:
            invitation = Invitation.custom_manager.select_for_update().get(token=token)
            if invitation.is_accepted:
                raise InvitationAlreadyAcceptedError('Invitation already accepted')

            # Validate the token
            if invitation.token != token:
                raise InvitationTokenMismatchError("Invitation Code Doesn't Match")

        except Invitation.DoesNotExist:
            raise InvitationNotFoundError('Invitation not found')

        try:
            user = User.objects.get(email=invitation.email)
        except User.DoesNotExist:
            raise TypeError(f'User with email {invitation.email} not found')

        user.tenant.add(invitation.tenant)
        invitation.is_accepted = True
        invitation.accepted_at = timezone.now()
        invitation.save()
        return user

class Invitation(models.Model):
    tenant = models.ForeignKey('tenants.Tenant', related_name='invitations', on_delete=models.CASCADE)
    email = models.EmailField()
    token = models.CharField(max_length=6, null=False)
    invited_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_invitations', null=True, blank=True)
    is_accepted = models.BooleanField(default=False)
    accepted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    custom_manager = InvitationManager()

    class Meta:
            unique_together = ('tenant', 'email')

import os

from django.contrib.auth.models import Permission
from django.core.management import call_command
from django.db import IntegrityError, transaction
from django.http import HttpResponseRedirect
from django.utils.encoding import smart_str
from django.utils.http import urlsafe_base64_decode
from django_tenants.utils import schema_context
from rest_framework import permissions, status
from rest_framework.exceptions import NotFound
from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication.utils import Util
from tenants.models import Invitation, Tenant
from tenants.serializers import (
    InvitationSerializer,
    InvitationUpdateSerializer,
    TenantSerializer,
)
from tenants.utils import Utils
from tenant_permissions.models import Role, UserRoles


class CustomRedirect(HttpResponseRedirect):
    allowed_schemes = [os.environ.get("APP_SCHEME"), "http", "https"]


class TenantCreateAPIView(ListCreateAPIView):
    serializer_class = TenantSerializer
    queryset = Tenant.objects.all()
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return self.request.user.tenant.all()

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        serializer = TenantSerializer(data=request.data)

        if serializer.is_valid():
            saved_tenant = serializer.save(admin_email=self.request.user)
            savedInvitation = Invitation.custom_manager.create_invitation(
                email=request.user.email, tenant=saved_tenant
            )

            redirect_url = request.data.get("redirect_url", "")

            url = Utils.generate_invitation_url(
                request=request,
                invitation=savedInvitation,
                redirect_url=redirect_url,
                fallback_url=request.data.get("fallback_url", ""),
            )

            data = {
                "email_body": url,
                "to_email": request.user.email,
                "email_subject": "Accept The Invitation",
                "title": "Accept The Invitation",
                "call_to_action_message": "Accept The Invitation",
                "confirmation_url": url,
                "button_text": "Accept The Invitation",
                "information_message": "Button not working? Copy and paste this link into your browser:",
            }

            Util.send_email(data)

            with schema_context(saved_tenant.schema_name):
                tenant_admin_role, created = Role.objects.get_or_create(
                    name="TENANT_ADMIN"
                )
                permissions = Permission.objects.filter(
                    codename__in=["can_change_tenant_info"]
                )
                tenant_admin_role.permissions.add(*permissions)
                user_roles, _ = UserRoles.objects.get_or_create(user=request.user)
                user_roles.roles.add(tenant_admin_role)
                user_roles.save()
                call_command("loaddata", "asset_type.json")
                call_command("loaddata", "complience_options.json")
            return Response(
                {
                    "data": f"we have sent you an invitation with the information.",
                    "tenant": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InviteUserAPIView(APIView):
    serializer_class = InvitationSerializer
    queryset = Invitation.custom_manager.all()

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        redirect_url = request.data.get("redirect_url", "")
        fallback_url = request.data.get("fallback_url", "")

        if serializer.is_valid():
            try:
                tenant = self.request.tenant
                saved_invitation = serializer.save(tenant=tenant)

                invitation_url = Utils.generate_invitation_url(
                    request=request,
                    invitation=saved_invitation,
                    redirect_url=redirect_url,
                    fallback_url=fallback_url,
                )

                response_data = serializer.data
                data = {
                    "to_email": request.data.get("email"),
                    "email_subject": "Accept The Invitation",
                    "title": "Accept The Invitation",
                    "general_message": "You have been invited to join {tenant.name}.",
                    "call_to_action_message": "Accept The Invitation",
                    "confirmation_url": invitation_url,
                    "button_text": "Accept The Invitation",
                    "information_message": "Button not working? Copy and paste this link into your browser:",
                }

                Util.send_email(data)
                return Response(data=response_data, status=status.HTTP_201_CREATED)

            except IntegrityError:
                return Response(
                    {"detail": "Invitation with this email already exists"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            except Exception as e:
                return Response(
                    {
                        "detail": f"An error occurred while processing the invitation.{e}"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AcceptInvitationAPI(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, token):
        redirect_url = request.query_params.get("redirect_url", "")
        fallback_url = request.query_params.get("fallback_url", "")
        token_id = smart_str(urlsafe_base64_decode(token))

        try:
            Invitation.custom_manager.accept_invitation(token=token_id)
            return CustomRedirect(f"{redirect_url}?token_valid=True")
        except TypeError:
            return CustomRedirect(
                f"{fallback_url}?token_valid=False&account_does_not_exist=True&accept_token={token}"
            )
        except Exception as e:
            return CustomRedirect(f"{fallback_url}?token_valid=False&exception={e}")


class InvitationAPIView(APIView):
    serializer_class = InvitationSerializer

    def get_queryset(self):
        return Invitation.custom_manager.filter(
            email=self.request.user.email, is_accepted=False
        )

    def get(self, request):
        invitations = self.get_queryset()
        serializer = self.serializer_class(invitations, many=True)
        return Response(serializer.data)


class UpdateInvitationAPIView(APIView):
    serializer_class = InvitationUpdateSerializer

    def get_invitation(self, token):
        try:
            invitation = Invitation.custom_manager.get(
                token=token, email=self.request.user.email
            )
        except Invitation.DoesNotExist:
            raise NotFound("Invitation not found or does not belong to you.")
        return invitation

    def patch(self, request, token, *args, **kwargs):
        invitation = self.get_invitation(token)

        # Update fields based on the request data
        serializer = self.serializer_class(invitation, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from rest_framework import serializers
from tenants.models import Tenant, Invitation
import uuid
from authentication.models import User
from rest_framework.exceptions import ValidationError


class TenantSerializer(serializers.ModelSerializer):
    schema_name = serializers.CharField(read_only=True)
    redirect_url = serializers.CharField(required=False, allow_blank=True)  # Allow empty
    admin_email = serializers.EmailField(read_only=True)

    class Meta:
        model = Tenant
        exclude = ('id',)

    def create(self, validated_data):
        validated_data['schema_name'] = str(uuid.uuid4())
        validated_data.pop('redirect_url', None)

        tenant = Tenant.objects.create(**validated_data)
        return tenant

class InvitationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    tenant = TenantSerializer(read_only=True)
    redirect_url = serializers.CharField(required=True, write_only=True)
    token = serializers.CharField(required=False, read_only=True)
    class Meta:
        model = Invitation
        fields = ['token','email', 'tenant', 'redirect_url']

    def validate(self, attrs):
        email = attrs.get('email')
        tenant = attrs.get('tenant')

        if Invitation.custom_manager.filter(email=email, tenant=tenant).exists():
            raise serializers.ValidationError("invitation already exist")

        return attrs

    def create(self, validated_data):
        email = validated_data['email']
        tenant = validated_data['tenant']
        return Invitation.custom_manager.create_invitation(email=email, tenant=tenant)

class AcceptInvitationSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)
    redirect_url = serializers.CharField(required=True)

    def create(self, validated_data):
        token=validated_data['token']
        try:
            return Invitation.custom_manager.accept_invitation(token=token)
        except TypeError as e:
            raise ValidationError({"detail": str(e)})
        except Exception as e:
            raise ValidationError({"detail": f"An error occurred while processing the invitation.{e}"})




class InvitationUpdateSerializer(serializers.ModelSerializer):
   class Meta:
        model = Invitation
        fields = ['is_accepted',]

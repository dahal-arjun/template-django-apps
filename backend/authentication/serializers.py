
from django.contrib.auth import authenticate
from django.core.exceptions import ObjectDoesNotExist
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib import auth

from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework.exceptions import ValidationError

from tenants.models import Tenant
from authentication.models import User
from tenants.serializers import TenantSerializer
from core import settings

class CheckAccountExistenceSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def create(self, validated_data):
        email = validated_data['email']
        return User.objects.check_user_with_email_exist(email=email)

class CreateAccountSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    middle_name = serializers.CharField(required=False, allow_blank=True)
    redirect_url = serializers.CharField(required=False, allow_blank=True)

    def create(self, validated_data):
        email = validated_data['email']
        password = validated_data['password']
        first_name = validated_data['first_name']
        last_name = validated_data['last_name']
        middle_name = validated_data['middle_name']
        
        try:
            return User.objects.create_user(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                middle_name=middle_name
            )
        except TypeError as e:
            raise ValidationError({"detail": str(e)})
        except Exception as e:
            raise ValidationError({"detail": "An error occurred while processing the invitation."})

class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255, min_length=3)
    password = serializers.CharField(max_length=68, min_length=6, write_only=True)
    tokens = serializers.SerializerMethodField()
    tenant = TenantSerializer(many=True, read_only=True)
    id = serializers.UUIDField(read_only=True)
    first_name = serializers.CharField(max_length=68, read_only=True)
    middle_name = serializers.CharField(max_length=68, read_only=True)
    last_name = serializers.CharField(max_length=68, read_only=True)


    def get_tokens(self, obj) -> dict:
        # Handle the case when `obj` is a dictionary (during validation)
        if isinstance(obj, dict):
            try:
                user = User.objects.get(email=obj.get('email'))
            except ObjectDoesNotExist:
                return {
                    'refresh': None,
                    'access': None
                }
        else:
            # Handle the case when `obj` is a User instance
            user = obj

        return {
            'refresh': user.tokens()['refresh'],
            'access': user.tokens()['access']
        }

    class Meta:
        model = User
        fields = ['id', 'email', 'password', 'tokens', 'tenant', 'middle_name', 'last_name', 'first_name' ]


    def validate(self, attrs: dict) -> dict:
        email = attrs.get('email', '')
        password = attrs.get('password', '')
        user = authenticate(email=email, password=password)

        if not user:
            raise AuthenticationFailed('Invalid credentials, try again')
        if not user.is_verified:
            raise AuthenticationFailed('Unverified email, try after verification')
        if not user.is_active:
            raise AuthenticationFailed('Account disabled, contact admin')

        return {
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'middle_name':user.middle_name,
            'last_name': user.last_name,
            'tokens': self.get_tokens(user),  # Updated to use the method
            'tenant': user.tenant
        }

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    default_error_message = {
        'bad_token': ('Token is expired or invalid')
    }

    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs

    def save(self, **kwargs):

        try:
            RefreshToken(self.token).blacklist()

        except TokenError:
            self.fail('bad_token')

class ResetPasswordEmailRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(min_length=2)

    redirect_url = serializers.CharField(max_length=500, required=False)

    class Meta:
        fields = ['email']

class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(
        min_length=6, max_length=68, write_only=True)
    token = serializers.CharField(
        min_length=1, write_only=True)
    uidb64 = serializers.CharField(
        min_length=1, write_only=True)

    class Meta:
        fields = ['password', 'token', 'uidb64']

    def validate(self, attrs):
        try:
            password = attrs.get('password')
            token = attrs.get('token')
            uidb64 = attrs.get('uidb64')

            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise AuthenticationFailed('The reset link is invalid', 401)

            user.set_password(password)
            user.save()

            return (user)
        except Exception as e:
            raise AuthenticationFailed('The reset link is invalid', 401)
        return super().validate(attrs)

class EmailVerificationSerializer(serializers.ModelSerializer):
    token = serializers.CharField(max_length=555)

    class Meta:
        model = User
        fields = ['token']

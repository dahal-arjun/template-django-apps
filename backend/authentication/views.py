import os

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.conf import settings


from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework.response import Response
from rest_framework import status, permissions
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from rest_framework_simplejwt.tokens import RefreshToken
import jwt

from authentication.models import User
from authentication.serializers import(
    CheckAccountExistenceSerializer,
    CreateAccountSerializer,
    LoginSerializer,
    LogoutSerializer,
    ResetPasswordEmailRequestSerializer,
    SetNewPasswordSerializer,
    EmailVerificationSerializer,
)

from authentication.tasks import send_verification_email



class CustomRedirect(HttpResponseRedirect):
    allowed_schemes = [os.environ.get('APP_SCHEME'), 'http', 'https']


class CheckAccountExistenceAPIView(CreateAPIView):
    serializer_class = CheckAccountExistenceSerializer

    def post(self, request, *args, **kwargs):
        serializer = CheckAccountExistenceSerializer(data=request.data)
        if serializer.is_valid():
            if serializer.save():
                return Response({"message":"Account Found"}, status=status.HTTP_200_OK)
            return Response({"message":"Account Not Found"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CreateAccountAPIView(CreateAPIView):
    serializer_class = CreateAccountSerializer
    permission_classes = (permissions.AllowAny,)
    def post(self, request, *args, **kwargs):
        serializer = CreateAccountSerializer(data=request.data)
        redirect_url = request.data.get('redirect_url', '')


        if serializer.is_valid():
            user = serializer.save()
            if user:
                token = RefreshToken.for_user(user).access_token
                current_site = get_current_site(request).domain
                relativeLink = reverse('email-verify')
                complete_url = 'http://'+current_site+relativeLink+"?token="+str(token)+"&redirect_url="+redirect_url
                data = {'to_email': user.email,
                        'email_subject': 'Verify Your Email',
                        'title': 'Verify Your Email',
                        'general_message': 'To get started, please verify your email address',
                        'call_to_action_message': 'In order to complete your registration, please click the button below:',
                        'confirmation_url': complete_url,
                        'button_text': 'Complete Registration',
                        'information_message': 'Button not working? Copy and paste this link into your browser',
                        }
                send_verification_email.delay(data)

                return Response({"message":"Registered Account"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyEmail(GenericAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = EmailVerificationSerializer
    @extend_schema(
            parameters=[
                OpenApiParameter(
                    name='token',
                    location=OpenApiParameter.QUERY,
                    description='Description',
                    type=str
                )
            ]
    )
    def get(self, request):
        token = request.GET.get('token')
        redirect_url = request.GET.get('redirect_url', '')

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user = User.objects.get(id=payload['user_id'])
            if not user.is_verified:
                user.is_verified = True
                user.save()
            
            if redirect_url:
                return CustomRedirect(f"{redirect_url}?access_token={user.tokens()['access']}&refresh_token={user.tokens()['refresh']}")
            else:
                return Response({'email': 'Successfully activated'}, status=status.HTTP_200_OK)
        except jwt.ExpiredSignatureError as identifier:
            return Response({'error': 'Activation Expired'}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.exceptions.DecodeError as identifier:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

class LoginAPIView(GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class LogoutAPIView(GenericAPIView):
    serializer_class = LogoutSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

class RequestPasswordResetEmail(GenericAPIView):
    serializer_class = ResetPasswordEmailRequestSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        email = request.data.get('email', '')

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            current_site = get_current_site(
                request=request).domain
            relativeLink = reverse(
                'password-reset-confirm', kwargs={'uidb64': uidb64, 'token': token})

            redirect_url = request.data.get('redirect_url', '')
            absurl = 'http://'+current_site + relativeLink
            complete_url = absurl+"?redirect_url="+redirect_url
            data = {
                'to_email': user.email,
                'email_subject': 'Reset Your Password',
                'title': 'Reset Your Password',
                'general_message': 'We received a request to reset your password. If you didn\'t make this request, you can ignore this message.',
                'call_to_action_message': 'To reset your password, simply click the button below:',
                'confirmation_url': complete_url,
                'button_text': 'Reset Your Password',
                'information_message': 'Button not working? Copy and paste this link into your browser:',
            }
            send_password_reset_email.delay(data)
        return Response({"message":"We Have Sent you an Email"}, status=status.HTTP_200_OK)

class PasswordTokenCheckAPI(GenericAPIView):
    serializer_class = SetNewPasswordSerializer
    permission_classes = (permissions.AllowAny,)

    @extend_schema(
        parameters=[
            OpenApiParameter(name='uidb64', type=str, description='User ID Base 64', location=OpenApiParameter.PATH, required=True),
            OpenApiParameter(name='token', type=str, description='Token', location=OpenApiParameter.PATH, required=True),
            OpenApiParameter(name='redirect_url', type=str, description='Redirect URL', location=OpenApiParameter.QUERY)
        ],
        responses={
            200: OpenApiResponse(description='Redirects based on token validity'),
            400: OpenApiResponse(description='Error response when token is invalid'),
        }
    )
    def get(self, request, uidb64, token):
        redirect_url = request.GET.get('redirect_url', '')

        try:
            id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                    return CustomRedirect(redirect_url+ '?token_valid=False')

            return CustomRedirect(redirect_url + '?token_valid=True&message=Credentials Valid&uidb64=' + uidb64 + '&token=' + token)

        except DjangoUnicodeDecodeError as identifier:
            try:
                if not PasswordResetTokenGenerator().check_token(user, token):
                    return CustomRedirect(redirect_url + '?token_valid=False')

            except UnboundLocalError as e:
                return CustomRedirect(redirect_url + '?token_valid=False')

class SetNewPasswordAPIView(GenericAPIView):
    serializer_class = SetNewPasswordSerializer
    permission_classes = (permissions.AllowAny,)

    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'success': True, 'message': 'Password reset success'}, status=status.HTTP_200_OK)

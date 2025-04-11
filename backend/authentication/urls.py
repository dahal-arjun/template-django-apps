from django.urls import path
from authentication.views import (
    CreateAccountAPIView,
    LoginAPIView,
    LogoutAPIView,
    PasswordTokenCheckAPI,
    RequestPasswordResetEmail,
    SetNewPasswordAPIView,
    VerifyEmail,
)
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

urlpatterns = [
    path('login/', LoginAPIView.as_view(), name="login"),
    path('create-account/', CreateAccountAPIView.as_view()),
    path('email-verify/', VerifyEmail.as_view(), name="email-verify"),

    path('logout/', LogoutAPIView.as_view(), name="logout"),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('request-reset-email/', RequestPasswordResetEmail.as_view(), name="request-reset-email"),
    path('password-reset/<uidb64>/<token>/', PasswordTokenCheckAPI.as_view(), name='password-reset-confirm'),
    path('password-reset-complete', SetNewPasswordAPIView.as_view(), name='password-reset-complete'),
]

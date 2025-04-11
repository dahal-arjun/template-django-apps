from django.urls import path, include

from tenants.views import (
    AcceptInvitationAPI,
    TenantCreateAPIView,
    InviteUserAPIView,
    InvitationAPIView,
    UpdateInvitationAPIView
)

urlpatterns = [
    path('', TenantCreateAPIView.as_view()),
    path('invite/', InviteUserAPIView.as_view()),
    path('invite/pending',InvitationAPIView.as_view()),
    path('invite/accept/manual/<str:token>/', UpdateInvitationAPIView.as_view(), name='invitation-update'),
    path('invite/accept/<str:token>/', AcceptInvitationAPI.as_view(), name='invitation-accept'),

]

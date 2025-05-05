from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.views import APIView
from rest_framework.response import Response

from rest_framework import serializers
from rest_framework import permissions

class HealthSerializer(serializers.Serializer):
    message = serializers.CharField()

class Health(APIView):
    serializer_class = HealthSerializer
    permission_classes = (permissions.AllowAny,)

    def get(self, request, *args, **kwargs):
        data = {"message": "Service is Running"}
        serializer = self.serializer_class(data)
        return Response(serializer.data)


urlpatterns = [
    path('api/tenants/', include("tenants.urls")),
    path('api/auth/', include("authentication.urls")),
    path('api/health/', Health.as_view(), name='health'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path("", include("tasks.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += [
        path('__debug__/', include('debug_toolbar.urls')),
    ]

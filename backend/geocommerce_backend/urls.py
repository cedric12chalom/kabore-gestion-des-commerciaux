"""
GeoCommerce Pro - URL Configuration
Routage principal de l'API REST
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenBlacklistView,
)

urlpatterns = [
    # Admin Django
    path('admin/', admin.site.urls),

    # Documentation API - Swagger/OpenAPI
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/docs/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # Authentication JWT
    path('api/v1/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/auth/logout/', TokenBlacklistView.as_view(), name='token_blacklist'),

    # Apps API
    path('api/v1/users/', include('apps.users.urls')),
    path('api/v1/commerciaux/', include('apps.commerciaux.urls')),
    path('api/v1/clients/', include('apps.clients.urls')),
    path('api/v1/gps/', include('apps.gps.urls')),
    path('api/v1/visites/', include('apps.visites.urls')),
    path('api/v1/commandes/', include('apps.commandes.urls')),
    path('api/v1/opportunites/', include('apps.opportunites.urls')),
    path('api/v1/dashboard/', include('apps.dashboard.urls')),
    path('api/v1/notifications/', include('apps.notifications.urls')),
]

# Servir les fichiers media en developpement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

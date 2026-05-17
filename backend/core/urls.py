"""
GeoCommerce Pro - URLs principales
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    # Admin Django
    path('admin/', admin.site.urls),

    # Documentation API (Swagger)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # Auth JWT
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Apps API v1
    path('api/v1/auth/', include('apps.users.urls')),
    path('api/v1/commerciaux/', include('apps.commerciaux.urls')),
    path('api/v1/clients/', include('apps.clients.urls')),
    path('api/v1/visites/', include('apps.visites.urls')),
    path('api/v1/gps/', include('apps.gps.urls')),
    path('api/v1/commandes/', include('apps.commandes.urls')),
    path('api/v1/dashboard/', include('apps.dashboard.urls')),
    path('api/v1/notifications/', include('apps.notifications.urls')),
]

# Fichiers médias en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

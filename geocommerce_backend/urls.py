"""
GeoCommerce Pro - Root URL Configuration
Mount des API :
  /api/v1/auth/   → authentification et sécurité du compte
  /api/v1/users/  → gestion CRUD des utilisateurs
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin Django
    path('admin/', admin.site.urls),

    # Authentification & sécurité du compte
    path('api/v1/auth/', include('apps.users.auth_urls')),

    # Gestion des utilisateurs
    path('api/v1/users/', include('apps.users.urls')),
]

# Fichiers média en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

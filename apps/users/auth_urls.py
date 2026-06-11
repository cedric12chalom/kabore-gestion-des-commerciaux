"""
URL Authentication : profile, mot de passe, déconnexion.
Séparé des URLs de gestion utilisateurs pour une meilleure organisation.
"""
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.users.views import (
    ProfileView,
    ChangePasswordView,
    logout_view,
    logout_all_view,
    me_view,
)
from apps.users.serializers import CustomTokenObtainPairSerializer


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


app_name = 'auth'

urlpatterns = [
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('logout/', logout_view, name='logout'),
    path('logout-all/', logout_all_view, name='logout_all'),
    path('me/', me_view, name='me'),
]

"""
URLs pour l'app users
"""
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    UserListView, UserDetailView, UserCreateView,
    ProfileView, ChangePasswordView,
    logout_view, logout_all_view, me_view,
)

urlpatterns = [
    # Auth JWT (utilise les serializers personnalisés via settings)
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Gestion utilisateurs
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/create/', UserCreateView.as_view(), name='user-create'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),

    # Profil & sécurité
    path('profile/', ProfileView.as_view(), name='profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('logout/', logout_view, name='logout'),
    path('logout-all/', logout_all_view, name='logout-all'),
    path('me/', me_view, name='me'),
]

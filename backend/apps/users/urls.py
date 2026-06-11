"""
URLs pour l'app users
Toutes les routes sont prefixees par /api/v1/auth/ (incluses via urls principal)
"""
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    UserListView, UserDetailView, UserCreateView,
    ProfileView, ChangePasswordView,
    logout_view, logout_all_view, me_view,
    CustomTokenObtainPairView,
)

urlpatterns = [
    # Auth JWT
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Gestion utilisateurs (prefixe /api/v1/auth/users/...)
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

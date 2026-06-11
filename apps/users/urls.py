"""
URL pour la gestion des utilisateurs (CRUD utilisateur par admin/manager).
Séparé des URLs d'authentification pour une meilleure organisation.
"""
from django.urls import path

from .views import UserListView, UserDetailView

app_name = 'users'

urlpatterns = [
    path('', UserListView.as_view(), name='user-list'),
    path('<int:pk>/', UserDetailView.as_view(), name='user-detail'),
]

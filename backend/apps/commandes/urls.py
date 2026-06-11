"""
URLs pour l'app commandes
"""
from django.urls import path
from .views import (
    CommandeListCreateView, CommandeDetailView,
    OpportuniteListCreateView, OpportuniteDetailView,
    pipeline_stats_view, livrer_commande_view,
)

urlpatterns = [
    path('', CommandeListCreateView.as_view(), name='commande-list'),
    path('<int:pk>/livrer/', livrer_commande_view, name='commande-livrer'),
    path('<int:pk>/', CommandeDetailView.as_view(), name='commande-detail'),
    path('opportunites/', OpportuniteListCreateView.as_view(), name='opportunite-list'),
    path('opportunites/<int:pk>/', OpportuniteDetailView.as_view(), name='opportunite-detail'),
    path('pipeline-stats/', pipeline_stats_view, name='pipeline-stats'),
]

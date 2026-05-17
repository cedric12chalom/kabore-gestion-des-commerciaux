"""
URLs pour l'app GPS
"""
from django.urls import path
from .views import (
    PositionListCreateView, PositionDetailView,
    HistoriqueParcoursView, AlerteZoneListView,
    positions_temps_reel_view, replay_parcours_view, sync_offline_view,
)

urlpatterns = [
    path('positions/', PositionListCreateView.as_view(), name='gps-position-list'),
    path('positions/<int:pk>/', PositionDetailView.as_view(), name='gps-position-detail'),
    path('parcours/', HistoriqueParcoursView.as_view(), name='gps-parcours'),
    path('alertes/', AlerteZoneListView.as_view(), name='gps-alertes'),
    path('temps-reel/', positions_temps_reel_view, name='gps-temps-reel'),
    path('replay/<int:commercial_id>/', replay_parcours_view, name='gps-replay'),
    path('sync/', sync_offline_view, name='gps-sync'),
]

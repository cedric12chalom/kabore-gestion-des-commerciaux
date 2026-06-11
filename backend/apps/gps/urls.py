from django.urls import path
from .views import (
    positions_actuelles_view,
    historique_parcours_view,
    commerciaux_proches_view,
    alertes_zone_view,
    positions_temps_reel_view,
)

urlpatterns = [
    path('positions-actuelles/', positions_actuelles_view, name='gps-positions-actuelles'),
    path('temps-reel/', positions_temps_reel_view, name='gps-temps-reel'),
    path('<int:commercial_id>/historique-parcours/', historique_parcours_view, name='gps-historique'),
    path('commerciaux-proches/', commerciaux_proches_view, name='gps-commerciaux-proches'),
    path('alertes/', alertes_zone_view, name='gps-alertes'),
]

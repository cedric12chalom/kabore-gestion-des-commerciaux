"""
URLs pour l'app dashboard
"""
from django.urls import path
from .views import dashboard_manager_view, dashboard_commercial_view, rapports_view, export_rapport_view

urlpatterns = [
    path('manager/', dashboard_manager_view, name='dashboard-manager'),
    path('commercial/', dashboard_commercial_view, name='dashboard-commercial'),
    path('rapports/', rapports_view, name='dashboard-rapports'),
    path('export/', export_rapport_view, name='dashboard-export'),
]

"""
URLs pour l'app visites
"""
from django.urls import path
from .views import VisiteListCreateView, VisiteDetailView, checkin_view, checkout_view, calendrier_view

urlpatterns = [
    path('', VisiteListCreateView.as_view(), name='visite-list'),
    path('<int:pk>/', VisiteDetailView.as_view(), name='visite-detail'),
    path('<int:visite_id>/checkin/', checkin_view, name='visite-checkin'),
    path('<int:visite_id>/checkout/', checkout_view, name='visite-checkout'),
    path('calendrier/', calendrier_view, name='visite-calendrier'),
]

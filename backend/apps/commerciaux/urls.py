"""
URLs pour l'app commerciaux
"""
from django.urls import path
from .views import (
    CommercialListView, CommercialDetailView, CommercialCreateView,
    TelephoneListCreateView, TelephoneDetailView,
    ZoneListCreateView, ZoneDetailView,
    ObjectifListCreateView,
    ProduitListCreateView, ProduitDetailView,
    commerciaux_actifs_view, clients_proches_view,
)

urlpatterns = [
    # Commerciaux
    path('', CommercialListView.as_view(), name='commercial-list'),
    path('create/', CommercialCreateView.as_view(), name='commercial-create'),
    path('<int:pk>/', CommercialDetailView.as_view(), name='commercial-detail'),

    # Téléphones
    path('<int:commercial_id>/telephones/', TelephoneListCreateView.as_view(), name='telephone-list'),
    path('telephones/<int:pk>/', TelephoneDetailView.as_view(), name='telephone-detail'),

    # Zones
    path('zones/', ZoneListCreateView.as_view(), name='zone-list'),
    path('zones/<int:pk>/', ZoneDetailView.as_view(), name='zone-detail'),

    # Objectifs
    path('objectifs/', ObjectifListCreateView.as_view(), name='objectif-list'),

    # Produits
    path('produits/', ProduitListCreateView.as_view(), name='produit-list'),
    path('produits/<int:pk>/', ProduitDetailView.as_view(), name='produit-detail'),

    # Endpoints spéciaux
    path('actifs/', commerciaux_actifs_view, name='commerciaux-actifs'),
    path('<int:commercial_id>/clients-proches/', clients_proches_view, name='clients-proches'),
]

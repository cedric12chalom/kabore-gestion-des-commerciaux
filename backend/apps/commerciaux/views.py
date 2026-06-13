"""
Views pour Commerciaux, Téléphones, Zones, Objectifs, Produits
"""
from rest_framework import generics, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q, Count, Sum, Avg
from django_filters.rest_framework import DjangoFilterBackend
from django.conf import settings
from apps.core.gis import Point

from apps.gps.models import PositionTempsReel
from .models import Commercial, Telephone, Zone, ZoneAssignee, ObjectifCommercial, Produit
from .serializers import (
    CommercialListSerializer, CommercialDetailSerializer, CommercialCreateSerializer,
    TelephoneSerializer, ZoneSerializer, ObjectifSerializer, ProduitSerializer,
)
from apps.users.permissions import IsAdminOrManager, IsCommercial, RoleBasedPermission


class CommercialListView(generics.ListAPIView):
    """GET /api/v1/commerciaux/ - Liste avec recherche et filtres"""
    serializer_class = CommercialListSerializer
    permission_classes = [IsAdminOrManager]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['statut', 'manager']
    search_fields = ['matricule', 'user__first_name', 'user__last_name', 'user__email']
    ordering_fields = ['created_at', 'user__last_name']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        qs = Commercial.objects.select_related('user', 'manager').prefetch_related('telephones')

        if user.is_admin:
            return qs.annotate(
                ca_total=Sum('commandes__montant_total'),
            )

        if user.is_manager:
            return qs.filter(
                Q(user=user) | Q(user__manager=user)
            ).annotate(
                ca_total=Sum('commandes__montant_total'),
            )

        return qs.filter(user=user)


class CommercialDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET/PUT/PATCH/DELETE /api/v1/commerciaux/<id>/"""
    serializer_class = CommercialDetailSerializer
    permission_classes = [IsAdminOrManager]
    lookup_field = 'pk'

    def get_queryset(self):
        user = self.request.user
        qs = Commercial.objects.select_related('user', 'manager').prefetch_related('telephones', 'objectifs', 'zones_assignees')
        if user.is_admin:
            return qs
        if user.is_manager:
            return qs.filter(Q(user=user) | Q(user__manager=user))
        return qs.filter(user=user)

    def perform_destroy(self, instance):
        instance.statut = 'INACTIF'
        instance.save()


class CommercialCreateView(generics.CreateAPIView):
    """POST /api/v1/commerciaux/"""
    serializer_class = CommercialCreateSerializer
    permission_classes = [IsAdminOrManager]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class TelephoneListCreateView(generics.ListCreateAPIView):
    """GET/POST /api/v1/commerciaux/<commercial_id>/telephones/"""
    serializer_class = TelephoneSerializer
    permission_classes = [IsAdminOrManager]

    def get_queryset(self):
        commercial_id = self.kwargs.get('commercial_id')
        return Telephone.objects.filter(commercial_id=commercial_id)

    def perform_create(self, serializer):
        commercial_id = self.kwargs.get('commercial_id')
        commercial = Commercial.objects.get(id=commercial_id)
        serializer.save(commercial=commercial)


class TelephoneDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET/PUT/DELETE /api/v1/commerciaux/telephones/<id>/"""
    serializer_class = TelephoneSerializer
    permission_classes = [IsAdminOrManager]
    queryset = Telephone.objects.all()


# ========== ZONES ==========

class ZoneListCreateView(generics.ListCreateAPIView):
    """GET/POST /api/v1/commerciaux/zones/"""
    serializer_class = ZoneSerializer
    permission_classes = [IsAdminOrManager]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['ville', 'pays', 'is_active']
    search_fields = ['nom', 'ville']

    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return Zone.objects.all()
        return Zone.objects.filter(manager=user)


class ZoneDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET/PUT/DELETE /api/v1/commerciaux/zones/<id>/"""
    serializer_class = ZoneSerializer
    permission_classes = [IsAdminOrManager]

    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return Zone.objects.all()
        return Zone.objects.filter(manager=user)


# ========== OBJECTIFS ==========

class ObjectifListCreateView(generics.ListCreateAPIView):
    """GET/POST /api/v1/commerciaux/objectifs/"""
    serializer_class = ObjectifSerializer
    permission_classes = [IsAdminOrManager]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['commercial', 'periode', 'is_atteint']

    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return ObjectifCommercial.objects.all()
        if user.is_manager:
            return ObjectifCommercial.objects.filter(
                Q(commercial__user=user) | Q(commercial__user__manager=user)
            )
        return ObjectifCommercial.objects.filter(commercial__user=user)


# ========== PRODUITS ==========

class ProduitListCreateView(generics.ListCreateAPIView):
    """GET/POST /api/v1/commerciaux/produits/"""
    serializer_class = ProduitSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['categorie', 'is_active']
    search_fields = ['reference', 'nom', 'description']
    queryset = Produit.objects.filter(is_active=True)


class ProduitDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET/PUT/DELETE /api/v1/commerciaux/produits/<id>/"""
    serializer_class = ProduitSerializer
    queryset = Produit.objects.all()

    def get_permissions(self):
        if self.request.method in ('GET', 'HEAD', 'OPTIONS'):
            return [IsAuthenticated()]
        return [IsAdminOrManager()]


# ========== ENDPOINTS SPÉCIAUX ==========

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def commerciaux_actifs_view(request):
    """GET /api/v1/commerciaux/actifs/ - Commerciaux actuellement en ligne (position récente)"""
    positions = PositionTempsReel.objects.filter(online=True).select_related('commercial', 'commercial__user')
    data = []
    for pos in positions:
        data.append({
            'id': pos.commercial_id,
            'nom': pos.commercial.nom_complet,
            'matricule': pos.commercial.matricule,
            'position': {
                'lat': pos.latitude,
                'lng': pos.longitude,
                'timestamp': pos.dernier_update.isoformat(),
            },
        })
    return Response({'success': True, 'count': len(data), 'commerciaux': data})

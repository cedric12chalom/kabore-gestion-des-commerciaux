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

if settings.USE_GIS:
    from django.contrib.gis.db.models.functions import Distance
else:
    Distance = None

from .models import Commercial, Telephone, Zone, ObjectifCommercial, Produit
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
    filterset_fields = ['statut', 'zone', 'user__manager']
    search_fields = ['matricule', 'user__first_name', 'user__last_name', 'user__email']
    ordering_fields = ['created_at', 'user__last_name', 'objectif_mensuel']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        qs = Commercial.objects.select_related('user', 'zone').prefetch_related('telephones')

        if user.is_admin:
            return qs.annotate(
                total_visites=Count('visites'),
                ca_total=Sum('commandes__montant_total'),
            )

        if user.is_manager:
            return qs.filter(
                Q(user=user) | Q(user__manager=user)
            ).annotate(
                total_visites=Count('visites'),
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
        qs = Commercial.objects.select_related('user', 'zone').prefetch_related('telephones', 'objectifs')
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
    permission_classes = [IsAdminOrManager]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['categorie', 'is_active']
    search_fields = ['reference', 'nom', 'description']
    queryset = Produit.objects.all()


class ProduitDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET/PUT/DELETE /api/v1/commerciaux/produits/<id>/"""
    serializer_class = ProduitSerializer
    permission_classes = [IsAdminOrManager]
    queryset = Produit.objects.all()


# ========== ENDPOINTS SPÉCIAUX ==========

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def commerciaux_actifs_view(request):
    """GET /api/v1/commerciaux/actifs/ - Commerciaux actuellement en ligne (position récente)"""
    from django.utils import timezone
    from datetime import timedelta
    from apps.gps.models import PositionGPS

    # Commerciaux avec position dans les 5 dernières minutes
    limite = timezone.now() - timedelta(minutes=5)

    commerciaux_ids = PositionGPS.objects.filter(
        timestamp__gte=limite
    ).values_list('commercial_id', flat=True).distinct()

    commerciaux = Commercial.objects.filter(
        id__in=commerciaux_ids,
        statut='ACTIF'
    ).select_related('user')

    data = []
    for com in commerciaux:
        last_pos = PositionGPS.objects.filter(commercial=com).order_by('-timestamp').first()
        data.append({
            'id': com.id,
            'nom': com.nom_complet,
            'matricule': com.matricule,
            'position': {
                'lat': float(last_pos.latitude) if last_pos else None,
                'lng': float(last_pos.longitude) if last_pos else None,
                'timestamp': last_pos.timestamp.isoformat() if last_pos else None,
            } if last_pos else None,
        })

    return Response({'success': True, 'count': len(data), 'commerciaux': data})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def clients_proches_view(request, commercial_id):
    """GET /api/v1/commerciaux/<id>/clients-proches/ - Clients les plus proches du commercial"""
    from apps.clients.models import Client
    from apps.gps.models import PositionGPS
    from django.contrib.gis.measure import D

    try:
        commercial = Commercial.objects.get(id=commercial_id)
    except Commercial.DoesNotExist:
        return Response({'success': False, 'error': 'Commercial non trouvé'}, status=404)

    # Dernière position du commercial
    last_pos = PositionGPS.objects.filter(commercial=commercial).order_by('-timestamp').first()
    if not last_pos or not last_pos.position:
        return Response({'success': False, 'error': 'Position GPS non disponible'}, status=400)

    # Clients dans un rayon de 10km
    clients = Client.objects.filter(
        is_actif=True,
        position__isnull=False,
        position__distance_lte=(last_pos.position, D(km=10))
    ).annotate(
        distance=Distance('position', last_pos.position)
    ).order_by('distance')[:20]

    data = []
    for client in clients:
        data.append({
            'id': client.id,
            'raison_sociale': client.raison_sociale,
            'distance_m': round(client.distance.m, 0),
            'distance_km': round(client.distance.km, 2),
            'adresse': client.adresse,
            'ville': client.ville,
            'position': {'lat': client.latitude, 'lng': client.longitude},
        })

    return Response({'success': True, 'clients': data})

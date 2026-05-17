"""
Views pour Clients
"""
from rest_framework import generics, filters, serializers
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count, Sum
from django_filters.rest_framework import DjangoFilterBackend
from django.conf import settings
from apps.core.gis import Point

if settings.USE_GIS:
    from django.contrib.gis.db.models.functions import Distance
else:
    Distance = None

from .models import Client
from apps.users.permissions import IsAdminOrManager, IsCommercial, RoleBasedPermission


class ClientSerializer(serializers.ModelSerializer):
    """Serializer inline pour éviter import circulaire"""
    commercial_nom = serializers.CharField(source='commercial_referent.nom_complet', read_only=True)
    nombre_visites = serializers.IntegerField(read_only=True)
    ca_total = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    latitude = serializers.FloatField(read_only=True)
    longitude = serializers.FloatField(read_only=True)

    class Meta:
        model = Client
        fields = [
            'id', 'raison_sociale', 'nom_contact', 'email', 'telephone',
            'adresse', 'ville', 'code_postal', 'pays',
            'position', 'latitude', 'longitude',
            'secteur', 'potentiel',
            'commercial_referent', 'commercial_nom',
            'is_actif', 'nombre_visites', 'ca_total',
            'notes', 'date_creation', 'date_modification',
        ]
        read_only_fields = ['date_creation', 'date_modification']


class ClientListCreateView(generics.ListCreateAPIView):
    """GET/POST /api/v1/clients/"""
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['ville', 'secteur', 'potentiel', 'is_actif', 'commercial_referent']
    search_fields = ['raison_sociale', 'nom_contact', 'email', 'telephone', 'ville']
    ordering_fields = ['date_creation', 'raison_sociale', 'ville']
    ordering = ['-date_creation']

    def get_queryset(self):
        user = self.request.user
        qs = Client.objects.annotate(
            nombre_visites=Count('visites'),
            ca_total=Sum('commandes__montant_total'),
        )

        if user.is_admin:
            return qs
        if user.is_manager:
            return qs.filter(
                Q(commercial_referent__user=user) | 
                Q(commercial_referent__user__manager=user)
            )
        if user.is_commercial:
            return qs.filter(commercial_referent__user=user)

        return qs.none()


class ClientDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET/PUT/DELETE /api/v1/clients/<id>/"""
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'

    def get_queryset(self):
        user = self.request.user
        qs = Client.objects.annotate(
            nombre_visites=Count('visites'),
            ca_total=Sum('commandes__montant_total'),
        )

        if user.is_admin:
            return qs
        if user.is_manager:
            return qs.filter(
                Q(commercial_referent__user=user) | 
                Q(commercial_referent__user__manager=user)
            )
        return qs.filter(commercial_referent__user=user)

    def perform_destroy(self, instance):
        instance.is_actif = False
        instance.save()


# Import serializers ici pour éviter les imports circulaires au niveau module
from rest_framework import serializers
from .models import Client

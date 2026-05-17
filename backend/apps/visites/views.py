"""
Views pour Visites et Rapports
"""
from rest_framework import generics, status, filters, serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q, Count, Avg
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from datetime import timedelta

from .models import Visite, RapportVisite
from apps.users.permissions import IsAdminOrManager, IsCommercial, RoleBasedPermission


class VisiteSerializer(serializers.ModelSerializer):
    """Serializer inline"""
    commercial_nom = serializers.CharField(source='commercial.nom_complet', read_only=True)
    client_nom = serializers.CharField(source='client.raison_sociale', read_only=True)
    client_position = serializers.SerializerMethodField()
    statut_display = serializers.CharField(source='get_statut_display', read_only=True)
    type_display = serializers.CharField(source='get_type_visite_display', read_only=True)
    is_validee = serializers.BooleanField(read_only=True)
    distance_checkin = serializers.FloatField(source='distance_checkin_client', read_only=True)

    class Meta:
        model = Visite
        fields = [
            'id', 'commercial', 'commercial_nom', 'client', 'client_nom', 'client_position',
            'type_visite', 'type_display', 'date_prevue', 'date_effective',
            'duree_estimee', 'duree_reelle', 'objectif',
            'statut', 'statut_display', 'is_validee',
            'checkin_lat', 'checkin_lng', 'checkin_timestamp',
            'checkout_lat', 'checkout_lng', 'checkout_timestamp',
            'compte_rendu', 'actions_suivantes', 'satisfaction_client',
            'distance_checkin',
            'created_at', 'updated_at',
        ]

    def get_client_position(self, obj):
        if obj.client.position:
            return {'lat': obj.client.latitude, 'lng': obj.client.longitude}
        return None


class VisiteListCreateView(generics.ListCreateAPIView):
    """GET/POST /api/v1/visites/"""
    serializer_class = VisiteSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['statut', 'type_visite', 'commercial', 'client', 'date_prevue']
    search_fields = ['client__raison_sociale', 'objectif', 'compte_rendu']
    ordering_fields = ['date_prevue', 'date_effective', 'statut']
    ordering = ['-date_prevue']

    def get_queryset(self):
        user = self.request.user
        qs = Visite.objects.select_related('commercial', 'client')

        if user.is_admin:
            return qs
        if user.is_manager:
            return qs.filter(
                Q(commercial__user=user) | Q(commercial__user__manager=user)
            )
        return qs.filter(commercial__user=user)

    def perform_create(self, serializer):
        visite = serializer.save()
        # Mettre à jour la dernière visite du commercial
        visite.commercial.derniere_visite = timezone.now()
        visite.commercial.save()


class VisiteDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET/PUT/DELETE /api/v1/visites/<id>/"""
    serializer_class = VisiteSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'

    def get_queryset(self):
        user = self.request.user
        qs = Visite.objects.select_related('commercial', 'client')
        if user.is_admin:
            return qs
        if user.is_manager:
            return qs.filter(
                Q(commercial__user=user) | Q(commercial__user__manager=user)
            )
        return qs.filter(commercial__user=user)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def checkin_view(request, visite_id):
    """POST /api/v1/visites/<id>/checkin/ - Enregistrement check-in GPS"""
    try:
        visite = Visite.objects.get(id=visite_id)
    except Visite.DoesNotExist:
        return Response({'success': False, 'error': 'Visite non trouvée'}, status=404)

    # Vérifier permissions
    user = request.user
    if not (user.is_admin or user.is_manager or visite.commercial.user == user):
        return Response({'success': False, 'error': 'Permission refusée'}, status=403)

    lat = request.data.get('latitude')
    lng = request.data.get('longitude')
    precision = request.data.get('precision')

    if not lat or not lng:
        return Response({'success': False, 'error': 'Latitude et longitude requises'}, status=400)

    from django.contrib.gis.geos import Point

    visite.checkin_lat = lat
    visite.checkin_lng = lng
    visite.checkin_position = Point(float(lng), float(lat), srid=4326)
    visite.checkin_timestamp = timezone.now()
    visite.statut = Visite.Statut.EN_COURS
    visite.save()

    # Créer une position GPS
    from apps.gps.models import PositionGPS
    PositionGPS.objects.create(
        commercial=visite.commercial,
        position=Point(float(lng), float(lat), srid=4326),
        latitude=lat,
        longitude=lng,
        precision=precision,
        source='GPS',
    )

    return Response({
        'success': True,
        'message': 'Check-in enregistré',
        'distance_client_m': visite.distance_checkin_client,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def checkout_view(request, visite_id):
    """POST /api/v1/visites/<id>/checkout/ - Enregistrement check-out GPS"""
    try:
        visite = Visite.objects.get(id=visite_id)
    except Visite.DoesNotExist:
        return Response({'success': False, 'error': 'Visite non trouvée'}, status=404)

    user = request.user
    if not (user.is_admin or user.is_manager or visite.commercial.user == user):
        return Response({'success': False, 'error': 'Permission refusée'}, status=403)

    lat = request.data.get('latitude')
    lng = request.data.get('longitude')
    compte_rendu = request.data.get('compte_rendu', '')
    actions = request.data.get('actions_suivantes', '')
    satisfaction = request.data.get('satisfaction_client')

    if not lat or not lng:
        return Response({'success': False, 'error': 'Latitude et longitude requises'}, status=400)

    from django.contrib.gis.geos import Point

    visite.checkout_lat = lat
    visite.checkout_lng = lng
    visite.checkout_position = Point(float(lng), float(lat), srid=4326)
    visite.checkout_timestamp = timezone.now()

    # Calculer la durée réelle
    if visite.checkin_timestamp:
        duree = (visite.checkout_timestamp - visite.checkin_timestamp).total_seconds() / 60
        visite.duree_reelle = int(duree)

    visite.compte_rendu = compte_rendu
    visite.actions_suivantes = actions
    if satisfaction:
        visite.satisfaction_client = satisfaction

    visite.statut = Visite.Statut.EFFECTUEE
    visite.save()

    return Response({
        'success': True,
        'message': 'Check-out enregistré',
        'duree_reelle_min': visite.duree_reelle,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def calendrier_view(request):
    """GET /api/v1/visites/calendrier/ - Visites pour le calendrier (par mois)"""
    mois = request.query_params.get('mois')
    annee = request.query_params.get('annee')

    if not mois or not annee:
        now = timezone.now()
        mois = now.month
        annee = now.year

    user = request.user
    qs = Visite.objects.filter(
        date_prevue__month=mois,
        date_prevue__year=annee,
    ).select_related('commercial', 'client')

    if user.is_admin:
        pass
    elif user.is_manager:
        qs = qs.filter(Q(commercial__user=user) | Q(commercial__user__manager=user))
    else:
        qs = qs.filter(commercial__user=user)

    data = []
    for visite in qs:
        data.append({
            'id': visite.id,
            'titre': f"{visite.client.raison_sociale}",
            'date': visite.date_prevue.isoformat(),
            'statut': visite.statut,
            'type': visite.type_visite,
            'commercial': visite.commercial.nom_complet,
            'client': visite.client.raison_sociale,
        })

    return Response({'success': True, 'visites': data})


# Import serializers ici
from rest_framework import serializers
from .models import Visite, RapportVisite

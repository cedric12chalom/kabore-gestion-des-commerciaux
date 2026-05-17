"""
Views pour GPS temps réel, historique, alertes
"""
from rest_framework import generics, status, filters, serializers
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta, date
from django.conf import settings
from apps.core.gis import Point

if settings.USE_GIS:
    from django.contrib.gis.db.models.functions import Distance
else:
    Distance = None

from .models import PositionGPS, HistoriqueParcours, AlerteZone
from apps.users.permissions import IsAdminOrManager, IsCommercial


class GPSThrottle(UserRateThrottle):
    """Throttle spécifique pour les requêtes GPS fréquentes"""
    rate = '120/minute'


class PositionSerializer(serializers.ModelSerializer):
    """Serializer inline"""
    commercial_nom = serializers.CharField(source='commercial.nom_complet', read_only=True)

    class Meta:
        model = PositionGPS
        fields = [
            'id', 'commercial', 'commercial_nom',
            'latitude', 'longitude', 'position',
            'precision', 'altitude', 'vitesse', 'cap',
            'source', 'timestamp', 'is_sync',
            'date_enregistrement_local',
        ]
        read_only_fields = ['id', 'timestamp']


class PositionListCreateView(generics.ListCreateAPIView):
    """GET/POST /api/v1/gps/positions/"""
    serializer_class = PositionSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [GPSThrottle]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['timestamp']
    ordering = ['-timestamp']

    def get_queryset(self):
        user = self.request.user
        commercial_id = self.request.query_params.get('commercial')

        qs = PositionGPS.objects.select_related('commercial')

        if user.is_admin:
            if commercial_id:
                qs = qs.filter(commercial_id=commercial_id)
            return qs

        if user.is_manager:
            if commercial_id:
                qs = qs.filter(commercial_id=commercial_id)
            else:
                qs = qs.filter(
                    Q(commercial__user=user) | Q(commercial__user__manager=user)
                )
            return qs

        # Commercial : uniquement ses positions
        return qs.filter(commercial__user=user)

    def perform_create(self, serializer):
        """Enregistrement position GPS avec vérification zone"""
        user = self.request.user
        if user.is_commercial:
            commercial = user.commercial_profile
        else:
            commercial_id = self.request.data.get('commercial')
            from apps.commerciaux.models import Commercial
            commercial = Commercial.objects.get(id=commercial_id)

        position = serializer.save(commercial=commercial)

        # Vérifier sortie de zone
        if commercial.zone and commercial.zone.polygone:
            from django.contrib.gis.geos import GEOSGeometry
            zone_poly = commercial.zone.polygone
            if not zone_poly.contains(position.position):
                distance = position.position.distance(zone_poly.boundary)
                AlerteZone.objects.create(
                    commercial=commercial,
                    zone=commercial.zone,
                    type_alerte='SORTIE',
                    position=position.position,
                    distance_zone_m=distance,
                    message=f"{commercial.nom_complet} est sorti de la zone {commercial.zone.nom} ({distance:.0f}m)",
                )


class PositionDetailView(generics.RetrieveAPIView):
    """GET /api/v1/gps/positions/<id>/"""
    serializer_class = PositionSerializer
    permission_classes = [IsAuthenticated]
    queryset = PositionGPS.objects.all()


class HistoriqueParcoursView(generics.ListAPIView):
    """GET /api/v1/gps/parcours/ - Historique journalier"""
    serializer_class = serializers.ModelSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        class ParcoursSerializer(serializers.ModelSerializer):
            commercial_nom = serializers.CharField(source='commercial.nom_complet', read_only=True)

            class Meta:
                model = HistoriqueParcours
                fields = [
                    'id', 'commercial', 'commercial_nom', 'date',
                    'distance_totale_km', 'duree_totale_minutes',
                    'vitesse_moyenne_kmh', 'nombre_positions',
                    'trajectoire', 'premiere_position', 'derniere_position',
                    'created_at',
                ]
        return ParcoursSerializer

    def get_queryset(self):
        user = self.request.user
        qs = HistoriqueParcours.objects.select_related('commercial')

        commercial_id = self.request.query_params.get('commercial')
        date_debut = self.request.query_params.get('date_debut')
        date_fin = self.request.query_params.get('date_fin')

        if commercial_id:
            qs = qs.filter(commercial_id=commercial_id)

        if date_debut:
            qs = qs.filter(date__gte=date_debut)
        if date_fin:
            qs = qs.filter(date__lte=date_fin)

        if user.is_admin:
            return qs
        if user.is_manager:
            return qs.filter(
                Q(commercial__user=user) | Q(commercial__user__manager=user)
            )
        return qs.filter(commercial__user=user)


class AlerteZoneListView(generics.ListAPIView):
    """GET /api/v1/gps/alertes/"""
    permission_classes = [IsAdminOrManager]

    def get_serializer_class(self):
        class AlerteSerializer(serializers.ModelSerializer):
            commercial_nom = serializers.CharField(source='commercial.nom_complet', read_only=True)
            zone_nom = serializers.CharField(source='zone.nom', read_only=True)
            statut_display = serializers.CharField(source='get_statut_display', read_only=True)
            type_display = serializers.CharField(source='get_type_alerte_display', read_only=True)

            class Meta:
                model = AlerteZone
                fields = [
                    'id', 'commercial', 'commercial_nom', 'zone', 'zone_nom',
                    'type_alerte', 'type_display', 'statut', 'statut_display',
                    'position', 'distance_zone_m', 'message', 'timestamp',
                    'traite_par', 'date_traitement',
                ]
        return AlerteSerializer

    def get_queryset(self):
        user = self.request.user
        qs = AlerteZone.objects.select_related('commercial', 'zone')
        if user.is_admin:
            return qs
        return qs.filter(commercial__user__manager=user)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def positions_temps_reel_view(request):
    """GET /api/v1/gps/temps-reel/ - Dernières positions de tous les commerciaux"""
    limite = timezone.now() - timedelta(minutes=5)

    # Dernière position par commercial
    from django.db.models import Max

    user = request.user

    if user.is_admin:
        commerciaux_ids = PositionGPS.objects.filter(
            timestamp__gte=limite
        ).values('commercial').annotate(
            last_time=Max('timestamp')
        ).values_list('commercial', flat=True)
    elif user.is_manager:
        commerciaux_ids = PositionGPS.objects.filter(
            timestamp__gte=limite,
            commercial__user__manager=user,
        ).values('commercial').annotate(
            last_time=Max('timestamp')
        ).values_list('commercial', flat=True)
    else:
        commerciaux_ids = PositionGPS.objects.filter(
            timestamp__gte=limite,
            commercial__user=user,
        ).values('commercial').annotate(
            last_time=Max('timestamp')
        ).values_list('commercial', flat=True)

    positions = []
    for com_id in commerciaux_ids:
        pos = PositionGPS.objects.filter(commercial_id=com_id).order_by('-timestamp').first()
        if pos:
            positions.append({
                'commercial_id': pos.commercial_id,
                'commercial_nom': pos.commercial.nom_complet,
                'matricule': pos.commercial.matricule,
                'lat': float(pos.latitude),
                'lng': float(pos.longitude),
                'vitesse': pos.vitesse,
                'precision': pos.precision,
                'timestamp': pos.timestamp.isoformat(),
                'statut': pos.commercial.statut,
            })

    return Response({'success': True, 'count': len(positions), 'positions': positions})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def replay_parcours_view(request, commercial_id):
    """GET /api/v1/gps/replay/<commercial_id>/ - Replay d'un parcours journalier"""
    date_str = request.query_params.get('date')
    if not date_str:
        date_obj = timezone.now().date()
    else:
        date_obj = date.fromisoformat(date_str)

    positions = PositionGPS.objects.filter(
        commercial_id=commercial_id,
        timestamp__date=date_obj,
    ).order_by('timestamp')

    data = []
    for pos in positions:
        data.append({
            'lat': float(pos.latitude),
            'lng': float(pos.longitude),
            'timestamp': pos.timestamp.isoformat(),
            'vitesse': pos.vitesse,
            'precision': pos.precision,
        })

    return Response({
        'success': True,
        'date': date_str,
        'nombre_points': len(data),
        'parcours': data,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def sync_offline_view(request):
    """POST /api/v1/gps/sync/ - Synchronisation positions hors-ligne"""
    positions = request.data.get('positions', [])

    if not positions:
        return Response({'success': False, 'error': 'Aucune position à synchroniser'}, status=400)

    user = request.user
    if user.is_commercial:
        commercial = user.commercial_profile
    else:
        return Response({'success': False, 'error': 'Seuls les commerciaux peuvent envoyer des positions'}, status=403)

    created_count = 0
    for pos_data in positions:
        PositionGPS.objects.create(
            commercial=commercial,
            latitude=pos_data['latitude'],
            longitude=pos_data['longitude'],
            position=Point(pos_data['longitude'], pos_data['latitude'], srid=4326),
            precision=pos_data.get('precision'),
            vitesse=pos_data.get('vitesse'),
            source='GPS',
            is_sync=True,
            date_enregistrement_local=pos_data.get('timestamp'),
        )
        created_count += 1

    return Response({
        'success': True,
        'message': f'{created_count} positions synchronisées',
        'synchronized': created_count,
    })


# Import serializers
from rest_framework import serializers
from .models import PositionGPS, HistoriqueParcours, AlerteZone

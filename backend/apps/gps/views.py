"""
Views GPS temps réel
"""
from rest_framework import status, serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from django.db.models import Q

from apps.core.gis import distance_m, point_coords, Point
from .models import PositionTempsReel, HistoriqueParcours, AlerteZone
from apps.users.permissions import IsAdminOrManager


def _filter_positions_by_role(user):
    qs = PositionTempsReel.objects.select_related('commercial', 'commercial__user')
    if user.is_admin:
        return qs
    if user.is_manager:
        return qs.filter(Q(commercial__manager=user) | Q(commercial__user__manager=user))
    if hasattr(user, 'commercial_profile'):
        return qs.filter(commercial=user.commercial_profile)
    return qs.none()


def _serialize_position(pos: PositionTempsReel) -> dict:
    coords = point_coords(pos.position)
    lng, lat = coords if coords else (0, 0)
    return {
        'commercial_id': pos.commercial_id,
        'nom': pos.commercial.nom_complet,
        'matricule': pos.commercial.matricule,
        'lat': lat,
        'lng': lng,
        'accuracy': pos.precision,
        'speed': pos.vitesse,
        'heading': pos.cap,
        'online': pos.online,
        'timestamp': pos.dernier_update.isoformat(),
    }


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def positions_actuelles_view(request):
    """GET /api/v1/gps/positions-actuelles/"""
    positions = _filter_positions_by_role(request.user)
    for pos in positions:
        pos.marquer_offline_si_expire()
    data = [_serialize_position(p) for p in positions if p.online or request.user.is_admin or request.user.is_manager]
    return Response({'success': True, 'data': data})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def historique_parcours_view(request, commercial_id):
    """GET /api/v1/gps/<id>/historique-parcours/?jours=1"""
    jours = int(request.query_params.get('jours', 1))
    seuil = timezone.now() - timedelta(days=jours)

    user = request.user
    if user.is_commercial and user.commercial_profile.id != commercial_id:
        return Response({'success': False, 'error': 'Non autorisé'}, status=403)
    if user.is_manager:
        from apps.commerciaux.models import Commercial
        if not Commercial.objects.filter(id=commercial_id, manager=user).exists():
            return Response({'success': False, 'error': 'Non autorisé'}, status=403)

    points = HistoriqueParcours.objects.filter(
        commercial_id=commercial_id, timestamp__gte=seuil,
    ).order_by('timestamp')

    trace = []
    distance_totale = 0.0
    prev = None
    for p in points:
        coords = point_coords(p.position)
        if coords:
            trace.append({'lat': coords[1], 'lng': coords[0], 'timestamp': p.timestamp.isoformat()})
            if prev:
                d = distance_m(prev.position, p.position)
                if d:
                    distance_totale += d
            prev = p

    return Response({
        'success': True,
        'data': {
            'trace': trace,
            'distance_totale_km': round(distance_totale / 1000, 2),
            'nombre_points': len(trace),
        },
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminOrManager])
def commerciaux_proches_view(request):
    """GET /api/v1/gps/commerciaux-proches/?lat=&lng=&distance=5"""
    try:
        lat = float(request.query_params['lat'])
        lng = float(request.query_params['lng'])
        distance_km = float(request.query_params.get('distance', 5))
    except (KeyError, ValueError):
        return Response({'success': False, 'error': 'lat, lng requis'}, status=400)

    centre = Point(lng, lat, srid=4326)
    positions = _filter_positions_by_role(request.user).filter(online=True)
    result = []
    for pos in positions:
        d = distance_m(centre, pos.position)
        if d is not None and d <= distance_km * 1000:
            item = _serialize_position(pos)
            item['distance_km'] = round(d / 1000, 2)
            result.append(item)

    result.sort(key=lambda x: x['distance_km'])
    return Response({'success': True, 'data': result})


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminOrManager])
def alertes_zone_view(request):
    qs = AlerteZone.objects.select_related('commercial').order_by('-timestamp')[:50]
    if request.user.is_manager:
        qs = qs.filter(commercial__manager=request.user)
    return Response({'success': True, 'data': list(qs.values())})


# Alias rétrocompatibilité polling
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def positions_temps_reel_view(request):
    return positions_actuelles_view(request)

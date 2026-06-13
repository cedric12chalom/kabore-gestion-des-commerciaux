"""
Views pour Visites et Rapports
"""
from rest_framework import generics, status, filters, serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from datetime import timedelta
from apps.core.gis import Point

from .models import Visite, RapportVisite
from apps.users.permissions import IsAdminOrManager


def _position_from_request(request):
    lat = request.data.get('latitude')
    lng = request.data.get('longitude')
    if lat is not None and lng is not None:
        return Point(float(lng), float(lat), srid=4326)
    return None


class VisiteSerializer(serializers.ModelSerializer):
    manager_nom = serializers.CharField(source='manager.get_full_name', read_only=True)
    statut_display = serializers.CharField(source='get_statut_display', read_only=True)
    type_display = serializers.CharField(source='get_type_visite_display', read_only=True)
    is_validee = serializers.BooleanField(read_only=True)

    class Meta:
        model = Visite
        fields = [
            'id', 'manager', 'manager_nom',
            'point_vente_nom', 'contact_telephone', 'quartier', 'adresse_complete',
            'type_visite', 'type_display', 'date_prevue', 'date_effective',
            'duree_estimee', 'duree_reelle', 'objectif',
            'statut', 'statut_display', 'is_validee',
            'checkin_timestamp', 'checkout_timestamp',
            'compte_rendu', 'actions_suivantes', 'note_controle',
            'created_at', 'updated_at',
        ]

    def validate_manager(self, value):
        if value.role != 'MANAGER':
            raise serializers.ValidationError("Seul un manager peut être assigné à une visite.")
        return value

    def validate_date_prevue(self, value):
        if self.instance is None and value < timezone.now():
            raise serializers.ValidationError("Une visite ne peut pas être planifiée dans le passé.")
        return value

    def validate(self, attrs):
        user = self.context['request'].user
        manager = attrs.get('manager') or getattr(self.instance, 'manager', None)
        date_prevue = attrs.get('date_prevue') or getattr(self.instance, 'date_prevue', None)
        duree = attrs.get('duree_estimee') or getattr(self.instance, 'duree_estimee', 30)

        if user.is_manager and not user.is_admin:
            if manager and manager != user:
                raise serializers.ValidationError({
                    'manager': "Un manager ne peut planifier que ses propres visites."
                })
            attrs['manager'] = user

        if manager and date_prevue:
            start = date_prevue
            end = start + timedelta(minutes=duree or 30)
            qs = Visite.objects.filter(
                manager=manager,
                statut__in=[Visite.Statut.PLANIFIEE, Visite.Statut.EN_COURS],
                date_prevue__lt=end,
                date_prevue__gte=start - timedelta(minutes=duree or 30),
            )
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError({
                    'date_prevue': "Ce manager a déjà une visite sur ce créneau."
                })
        return attrs


class VisiteListCreateView(generics.ListCreateAPIView):
    """GET/POST /api/v1/visites/"""
    serializer_class = VisiteSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['statut', 'type_visite', 'manager', 'date_prevue']
    search_fields = ['point_vente_nom', 'quartier', 'objectif', 'compte_rendu']
    ordering_fields = ['date_prevue', 'date_effective', 'statut']
    ordering = ['-date_prevue']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsAdminOrManager()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        qs = Visite.objects.select_related('manager')

        if user.is_admin:
            return qs
        if user.is_manager:
            return qs.filter(manager=user)
        return qs.none()


class VisiteDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET/PUT/DELETE /api/v1/visites/<id>/"""
    serializer_class = VisiteSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'

    def get_permissions(self):
        if self.request.method in ('PUT', 'PATCH', 'DELETE'):
            return [IsAuthenticated(), IsAdminOrManager()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        qs = Visite.objects.select_related('manager')
        if user.is_admin:
            return qs
        if user.is_manager:
            return qs.filter(manager=user)
        return qs.none()


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminOrManager])
def checkin_view(request, visite_id):
    """POST /api/v1/visites/<id>/checkin/ — GPS navigateur du manager"""
    try:
        visite = Visite.objects.get(id=visite_id)
    except Visite.DoesNotExist:
        return Response({'success': False, 'error': 'Visite non trouvée'}, status=404)

    user = request.user
    if not (user.is_admin or visite.manager == user):
        return Response({'success': False, 'error': 'Permission refusée'}, status=403)

    if visite.statut != Visite.Statut.PLANIFIEE:
        return Response(
            {'success': False, 'error': 'La visite doit être planifiée pour démarrer le check-in'},
            status=400,
        )

    position = _position_from_request(request)
    if not position:
        return Response(
            {'success': False, 'error': 'Position GPS indisponible — activez la géolocalisation'},
            status=400,
        )

    visite.checkin_position = position
    visite.checkin_timestamp = timezone.now()
    visite.statut = Visite.Statut.EN_COURS
    visite.save()

    return Response({'success': True, 'message': 'Check-in enregistré'})


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminOrManager])
def checkout_view(request, visite_id):
    """POST /api/v1/visites/<id>/checkout/ — GPS navigateur du manager"""
    try:
        visite = Visite.objects.get(id=visite_id)
    except Visite.DoesNotExist:
        return Response({'success': False, 'error': 'Visite non trouvée'}, status=404)

    user = request.user
    if not (user.is_admin or visite.manager == user):
        return Response({'success': False, 'error': 'Permission refusée'}, status=403)

    compte_rendu = request.data.get('compte_rendu', '')
    actions = request.data.get('actions_suivantes', '')
    note = request.data.get('note_controle')

    if visite.statut != Visite.Statut.EN_COURS:
        return Response(
            {'success': False, 'error': 'La visite doit être en cours pour faire le check-out'},
            status=400,
        )

    position = _position_from_request(request)
    if not position:
        return Response({'success': False, 'error': 'Position GPS indisponible'}, status=400)

    visite.checkout_position = position
    visite.checkout_timestamp = timezone.now()
    visite.date_effective = timezone.now()

    if visite.checkin_timestamp:
        duree = (visite.checkout_timestamp - visite.checkin_timestamp).total_seconds() / 60
        visite.duree_reelle = int(duree)

    visite.compte_rendu = compte_rendu
    visite.actions_suivantes = actions
    if note:
        visite.note_controle = note

    visite.statut = Visite.Statut.EFFECTUEE
    visite.save()

    return Response({
        'success': True,
        'message': 'Check-out enregistré',
        'duree_reelle_min': visite.duree_reelle,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminOrManager])
def calendrier_view(request):
    """GET /api/v1/visites/calendrier/ — Visites pour le calendrier (par mois)"""
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
    ).select_related('manager')

    if user.is_manager and not user.is_admin:
        qs = qs.filter(manager=user)

    data = []
    for visite in qs:
        data.append({
            'id': visite.id,
            'titre': visite.point_vente_nom,
            'date': visite.date_prevue.isoformat(),
            'statut': visite.statut,
            'type': visite.type_visite,
            'manager': visite.manager.get_full_name(),
            'point_vente': visite.point_vente_nom,
        })

    return Response({'success': True, 'visites': data})

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
from apps.core.gis import Point

from .models import Visite, RapportVisite
from apps.users.permissions import IsAdminOrManager, IsCommercial, RoleBasedPermission


class VisiteSerializer(serializers.ModelSerializer):
    commercial_nom = serializers.CharField(source='commercial.nom_complet', read_only=True)
    statut_display = serializers.CharField(source='get_statut_display', read_only=True)
    type_display = serializers.CharField(source='get_type_visite_display', read_only=True)
    is_validee = serializers.BooleanField(read_only=True)

    class Meta:
        model = Visite
        fields = [
            'id', 'commercial', 'commercial_nom',
            'contact_nom', 'contact_telephone', 'quartier', 'adresse_complete',
            'type_visite', 'type_display', 'date_prevue', 'date_effective',
            'duree_estimee', 'duree_reelle', 'objectif',
            'statut', 'statut_display', 'is_validee',
            'checkin_timestamp', 'checkout_timestamp',
            'compte_rendu', 'actions_suivantes', 'satisfaction_client',
            'created_at', 'updated_at',
        ]

    def validate_date_prevue(self, value):
        if self.instance is None and value < timezone.now():
            raise serializers.ValidationError("Une visite ne peut pas etre planifiee dans le passe.")
        return value

    def validate(self, attrs):
        commercial = attrs.get('commercial') or getattr(self.instance, 'commercial', None)
        date_prevue = attrs.get('date_prevue') or getattr(self.instance, 'date_prevue', None)
        duree = attrs.get('duree_estimee') or getattr(self.instance, 'duree_estimee', 30)

        if commercial and date_prevue:
            start = date_prevue
            end = start + timedelta(minutes=duree or 30)
            qs = Visite.objects.filter(
                commercial=commercial,
                statut__in=[Visite.Statut.PLANIFIEE, Visite.Statut.EN_COURS],
                date_prevue__lt=end,
                date_prevue__gte=start - timedelta(minutes=duree or 30),
            )
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError({
                    'date_prevue': "Ce commercial a deja une visite sur ce creneau."
                })
        return attrs


class VisiteListCreateView(generics.ListCreateAPIView):
    """GET/POST /api/v1/visites/"""
    serializer_class = VisiteSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['statut', 'type_visite', 'commercial', 'date_prevue']
    search_fields = ['contact_nom', 'objectif', 'compte_rendu']
    ordering_fields = ['date_prevue', 'date_effective', 'statut']
    ordering = ['-date_prevue']

    def get_queryset(self):
        user = self.request.user
        qs = Visite.objects.select_related('commercial')

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
        qs = Visite.objects.select_related('commercial')
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
    if not (user.is_admin or visite.commercial.user == user or visite.commercial.user.manager == user):
        return Response({'success': False, 'error': 'Permission refusée'}, status=403)

    if visite.statut != Visite.Statut.PLANIFIEE:
        return Response({'success': False, 'error': 'La visite doit etre planifiee pour demarrer le check-in'}, status=400)

    from apps.gps.models import PositionTempsReel
    pos = PositionTempsReel.objects.filter(commercial=visite.commercial).first()
    if not pos:
        return Response({'success': False, 'error': 'Position GPS indisponible — activez le tracking'}, status=400)

    visite.checkin_position = pos.position
    visite.checkin_timestamp = timezone.now()
    visite.statut = Visite.Statut.EN_COURS
    visite.save()

    return Response({'success': True, 'message': 'Check-in enregistré'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def checkout_view(request, visite_id):
    """POST /api/v1/visites/<id>/checkout/ - Enregistrement check-out GPS"""
    try:
        visite = Visite.objects.get(id=visite_id)
    except Visite.DoesNotExist:
        return Response({'success': False, 'error': 'Visite non trouvée'}, status=404)

    user = request.user
    if not (user.is_admin or visite.commercial.user == user or visite.commercial.user.manager == user):
        return Response({'success': False, 'error': 'Permission refusée'}, status=403)

    compte_rendu = request.data.get('compte_rendu', '')
    actions = request.data.get('actions_suivantes', '')
    satisfaction = request.data.get('satisfaction_client')

    if visite.statut != Visite.Statut.EN_COURS:
        return Response({'success': False, 'error': 'La visite doit etre en cours pour faire le check-out'}, status=400)

    from apps.gps.models import PositionTempsReel
    pos = PositionTempsReel.objects.filter(commercial=visite.commercial).first()
    if not pos:
        return Response({'success': False, 'error': 'Position GPS indisponible'}, status=400)

    visite.checkout_position = pos.position
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
            'titre': visite.contact_nom,
            'date': visite.date_prevue.isoformat(),
            'statut': visite.statut,
            'type': visite.type_visite,
            'commercial': visite.commercial.nom_complet,
            'contact': visite.contact_nom,
        })

    return Response({'success': True, 'visites': data})


# Import serializers ici
from rest_framework import serializers
from .models import Visite, RapportVisite

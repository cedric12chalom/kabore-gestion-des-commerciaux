"""
Views pour Commandes et Opportunités
"""
import uuid
from decimal import Decimal

from rest_framework import generics, status, filters, serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import transaction
from django.db.models import Q, Sum, Count, Avg
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone

from .models import Commande, LigneCommande, Opportunite
from apps.commerciaux.models import Commercial, ObjectifCommercial
from apps.users.permissions import IsAdminOrManager, IsCommercial
from apps.core.gis import Point


class LigneCommandeSerializer(serializers.ModelSerializer):
    produit_nom = serializers.CharField(source='produit.nom', read_only=True)

    class Meta:
        model = LigneCommande
        fields = ['id', 'produit', 'produit_nom', 'quantite', 'prix_unitaire', 'remise', 'montant_ligne']
        read_only_fields = ['montant_ligne', 'produit_nom']


class CommandeSerializer(serializers.ModelSerializer):
    commercial_nom = serializers.CharField(source='commercial.nom_complet', read_only=True)
    lignes = LigneCommandeSerializer(many=True, read_only=True)

    class Meta:
        model = Commande
        fields = [
            'id', 'reference', 'commercial', 'commercial_nom', 'cree_par',
            'contact_nom', 'contact_telephone', 'quartier', 'adresse_complete',
            'date', 'date_livraison', 'montant_total', 'montant_remise',
            'statut', 'notes', 'lignes', 'created_at', 'updated_at',
        ]
        read_only_fields = ['reference', 'date', 'cree_par', 'date_livraison', 'created_at']


class CommandeCreateSerializer(serializers.ModelSerializer):
    lignes = LigneCommandeSerializer(many=True, write_only=True)

    class Meta:
        model = Commande
        fields = [
            'commercial', 'contact_nom', 'contact_telephone', 'quartier',
            'adresse_complete', 'notes', 'lignes',
        ]

    def validate(self, attrs):
        user = self.context['request'].user
        if not (user.is_admin or user.is_manager):
            raise serializers.ValidationError("Seuls Admin et Manager peuvent créer des commandes.")
        return attrs

    def create(self, validated_data):
        lignes_data = validated_data.pop('lignes')
        user = self.context['request'].user
        reference = f"CMD-{uuid.uuid4().hex[:8].upper()}"
        commande = Commande.objects.create(
            reference=reference,
            cree_par=user,
            statut=Commande.Statut.EN_COURS,
            **validated_data,
        )
        total = Decimal('0')
        for ligne_data in lignes_data:
            ligne = LigneCommande.objects.create(commande=commande, **ligne_data)
            total += ligne.montant_ligne
        commande.montant_total = total
        commande.save(update_fields=['montant_total'])
        return commande


class CommandeListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['statut', 'commercial', 'date']
    search_fields = ['reference', 'contact_nom', 'quartier', 'notes']
    ordering = ['-date']

    def get_serializer_class(self):
        return CommandeCreateSerializer if self.request.method == 'POST' else CommandeSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsAdminOrManager()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        qs = Commande.objects.select_related('commercial', 'cree_par').prefetch_related('lignes')
        if user.is_admin:
            return qs
        if user.is_manager:
            return qs.filter(Q(commercial__manager=user) | Q(commercial__user__manager=user))
        return qs.filter(commercial__user=user)


class CommandeDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CommandeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = Commande.objects.select_related('commercial').prefetch_related('lignes')
        if user.is_admin:
            return qs
        if user.is_manager:
            return qs.filter(Q(commercial__manager=user) | Q(commercial__user__manager=user))
        return qs.filter(commercial__user=user)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsCommercial])
def livrer_commande_view(request, pk):
    """POST /api/v1/commandes/<id>/livrer/ — Commercial owner uniquement."""
    try:
        commande = Commande.objects.select_related('commercial').get(pk=pk)
    except Commande.DoesNotExist:
        return Response({'success': False, 'error': 'Commande introuvable'}, status=404)

    if commande.commercial.user != request.user:
        return Response({'success': False, 'error': 'Non autorisé'}, status=403)

    if commande.statut != Commande.Statut.EN_COURS:
        return Response({'success': False, 'error': 'Statut invalide (EN_COURS requis)'}, status=400)

    from apps.gps.models import PositionTempsReel
    pos = PositionTempsReel.objects.filter(commercial=commande.commercial).first()
    if not pos:
        return Response({'success': False, 'error': 'Position GPS indisponible'}, status=400)

    with transaction.atomic():
        commande.statut = Commande.Statut.LIVREE
        commande.date_livraison = timezone.now()
        commande.position_livraison = pos.position
        commande.save()

        now = timezone.now()
        objectif, _ = ObjectifCommercial.objects.get_or_create(
            commercial=commande.commercial,
            periode=ObjectifCommercial.Periode.MENSUEL,
            annee=now.year,
            mois=now.month,
            defaults={'cible': Decimal('1')},
        )
        objectif.incrementer_realise(commande.montant_total)

    return Response({'success': True, 'data': CommandeSerializer(commande).data})


class OpportuniteSerializer(serializers.ModelSerializer):
    commercial_nom = serializers.CharField(source='commercial.nom_complet', read_only=True)

    class Meta:
        model = Opportunite
        fields = [
            'id', 'titre', 'description', 'commercial', 'commercial_nom',
            'contact_nom', 'contact_telephone', 'etape', 'probabilite',
            'montant_estime', 'montant_final', 'date_creation',
            'date_cloture_prevue', 'notes', 'created_at', 'updated_at',
        ]


class OpportuniteListCreateView(generics.ListCreateAPIView):
    serializer_class = OpportuniteSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['etape', 'commercial']
    search_fields = ['titre', 'contact_nom']

    def get_queryset(self):
        user = self.request.user
        qs = Opportunite.objects.select_related('commercial')
        if user.is_admin:
            return qs
        if user.is_manager:
            return qs.filter(Q(commercial__manager=user) | Q(commercial__user__manager=user))
        return qs.filter(commercial__user=user)


class OpportuniteDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OpportuniteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = Opportunite.objects.select_related('commercial')
        if user.is_admin:
            return qs
        if user.is_manager:
            return qs.filter(Q(commercial__manager=user) | Q(commercial__user__manager=user))
        return qs.filter(commercial__user=user)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def pipeline_stats_view(request):
    user = request.user
    qs = Opportunite.objects.all()
    if user.is_commercial:
        qs = qs.filter(commercial__user=user)
    elif user.is_manager:
        qs = qs.filter(Q(commercial__manager=user) | Q(commercial__user__manager=user))
    stats = qs.values('etape').annotate(
        count=Count('id'),
        montant_total=Sum('montant_estime'),
        probabilite_moyenne=Avg('probabilite'),
    )
    return Response({'success': True, 'pipeline': list(stats)})

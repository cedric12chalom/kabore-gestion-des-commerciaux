"""
Views pour Commandes, LignesCommande, Opportunités
"""
from rest_framework import generics, status, filters, serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q, Sum, Count, Avg
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone

from .models import Commande, LigneCommande, Opportunite
from apps.users.permissions import IsAdminOrManager, IsCommercial


class LigneCommandeSerializer(serializers.ModelSerializer):
    produit_nom = serializers.CharField(source='produit.nom', read_only=True)
    produit_reference = serializers.CharField(source='produit.reference', read_only=True)

    class Meta:
        model = LigneCommande
        fields = [
            'id', 'produit', 'produit_nom', 'produit_reference',
            'quantite', 'prix_unitaire', 'remise', 'montant_ligne',
        ]


class CommandeSerializer(serializers.ModelSerializer):
    """Serializer inline"""
    commercial_nom = serializers.CharField(source='commercial.nom_complet', read_only=True)
    client_nom = serializers.CharField(source='client.raison_sociale', read_only=True)
    statut_display = serializers.CharField(source='get_statut_display', read_only=True)
    lignes = LigneCommandeSerializer(many=True, read_only=True)
    nombre_articles = serializers.IntegerField(read_only=True)
    montant_ttc = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)

    class Meta:
        model = Commande
        fields = [
            'id', 'reference', 'commercial', 'commercial_nom',
            'client', 'client_nom', 'date', 'date_validation',
            'date_livraison_prevue', 'date_livraison_effective',
            'montant_total', 'montant_remise', 'montant_ht', 'tva',
            'montant_ttc', 'statut', 'statut_display',
            'adresse_livraison', 'notes',
            'lignes', 'nombre_articles',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['reference', 'date', 'created_at']


class CommandeCreateSerializer(serializers.ModelSerializer):
    """Serializer pour créer une commande avec ses lignes"""
    lignes = LigneCommandeSerializer(many=True, write_only=True)

    class Meta:
        model = Commande
        fields = [
            'client', 'date_livraison_prevue',
            'adresse_livraison', 'notes', 'lignes',
        ]

    def create(self, validated_data):
        lignes_data = validated_data.pop('lignes')

        # Générer une référence unique
        import uuid
        reference = f"CMD-{uuid.uuid4().hex[:8].upper()}"

        # Le commercial est l'utilisateur connecté
        user = self.context['request'].user
        commercial = user.commercial_profile

        commande = Commande.objects.create(
            reference=reference,
            commercial=commercial,
            **validated_data
        )

        total = 0
        for ligne_data in lignes_data:
            ligne = LigneCommande.objects.create(commande=commande, **ligne_data)
            total += ligne.montant_ligne

        commande.montant_total = total
        commande.montant_ht = total
        commande.save()

        return commande


class CommandeListCreateView(generics.ListCreateAPIView):
    """GET/POST /api/v1/commandes/"""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['statut', 'commercial', 'client', 'date']
    search_fields = ['reference', 'client__raison_sociale', 'notes']
    ordering_fields = ['date', 'montant_total', 'statut']
    ordering = ['-date']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CommandeCreateSerializer
        return CommandeSerializer

    def get_queryset(self):
        user = self.request.user
        qs = Commande.objects.select_related('commercial', 'client').prefetch_related('lignes')

        if user.is_admin:
            return qs
        if user.is_manager:
            return qs.filter(
                Q(commercial__user=user) | Q(commercial__user__manager=user)
            )
        return qs.filter(commercial__user=user)


class CommandeDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET/PUT/DELETE /api/v1/commandes/<id>/"""
    serializer_class = CommandeSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'

    def get_queryset(self):
        user = self.request.user
        qs = Commande.objects.select_related('commercial', 'client').prefetch_related('lignes')
        if user.is_admin:
            return qs
        if user.is_manager:
            return qs.filter(
                Q(commercial__user=user) | Q(commercial__user__manager=user)
            )
        return qs.filter(commercial__user=user)

    def perform_update(self, serializer):
        # Si le statut passe à VALIDEE, enregistrer la date
        instance = self.get_object()
        new_statut = self.request.data.get('statut')

        if new_statut == 'VALIDEE' and instance.statut != 'VALIDEE':
            serializer.save(date_validation=timezone.now())
        else:
            serializer.save()


# ========== OPPORTUNITÉS ==========

class OpportuniteSerializer(serializers.ModelSerializer):
    """Serializer inline"""
    commercial_nom = serializers.CharField(source='commercial.nom_complet', read_only=True)
    client_nom = serializers.CharField(source='client.raison_sociale', read_only=True)
    etape_display = serializers.CharField(source='get_etape_display', read_only=True)
    is_gagnee = serializers.BooleanField(read_only=True)
    is_perdue = serializers.BooleanField(read_only=True)

    class Meta:
        model = Opportunite
        fields = [
            'id', 'titre', 'description',
            'commercial', 'commercial_nom', 'client', 'client_nom',
            'etape', 'etape_display', 'probabilite',
            'montant_estime', 'montant_final',
            'date_creation', 'date_cloture_prevue', 'date_cloture_effective',
            'source', 'concurrence', 'notes', 'prochaine_action', 'date_prochaine_action',
            'is_gagnee', 'is_perdue',
            'created_at', 'updated_at',
        ]


class OpportuniteListCreateView(generics.ListCreateAPIView):
    """GET/POST /api/v1/commandes/opportunites/"""
    serializer_class = OpportuniteSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['etape', 'commercial', 'client', 'date_cloture_prevue']
    search_fields = ['titre', 'description', 'client__raison_sociale']
    ordering = ['-date_creation']

    def get_queryset(self):
        user = self.request.user
        qs = Opportunite.objects.select_related('commercial', 'client')

        if user.is_admin:
            return qs
        if user.is_manager:
            return qs.filter(
                Q(commercial__user=user) | Q(commercial__user__manager=user)
            )
        return qs.filter(commercial__user=user)


class OpportuniteDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET/PUT/DELETE /api/v1/commandes/opportunites/<id>/"""
    serializer_class = OpportuniteSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'

    def get_queryset(self):
        user = self.request.user
        qs = Opportunite.objects.select_related('commercial', 'client')
        if user.is_admin:
            return qs
        if user.is_manager:
            return qs.filter(
                Q(commercial__user=user) | Q(commercial__user__manager=user)
            )
        return qs.filter(commercial__user=user)


# ========== PIPELINE ==========

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def pipeline_stats_view(request):
    """GET /api/v1/commandes/pipeline-stats/ - Statistiques du pipeline"""
    user = request.user

    qs = Opportunite.objects.all()
    if user.is_commercial:
        qs = qs.filter(commercial__user=user)
    elif user.is_manager:
        qs = qs.filter(
            Q(commercial__user=user) | Q(commercial__user__manager=user)
        )

    stats = qs.values('etape').annotate(
        count=Count('id'),
        montant_total=Sum('montant_estime'),
        probabilite_moyenne=Avg('probabilite'),
    ).order_by('etape')

    return Response({'success': True, 'pipeline': list(stats)})


# Import serializers
from rest_framework import serializers
from .models import Commande, LigneCommande, Opportunite

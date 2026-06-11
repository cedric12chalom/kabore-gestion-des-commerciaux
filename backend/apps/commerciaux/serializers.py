"""
Serializers pour Commerciaux, Téléphones, Zones, Objectifs, Produits
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Commercial, Telephone, Zone, ZoneAssignee, ObjectifCommercial, Produit

User = get_user_model()


class TelephoneSerializer(serializers.ModelSerializer):
    """Serializer pour les téléphones d'un commercial"""
    type_display = serializers.CharField(source='get_type_display', read_only=True)

    class Meta:
        model = Telephone
        fields = ['id', 'numero', 'type', 'type_display', 'is_principal', 'is_whatsapp', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_numero(self, value):
        """Validation unicité du téléphone au sein du commercial"""
        value = value.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
        if not value.startswith('+'):
            raise serializers.ValidationError("Le numéro doit inclure l'indicatif international (ex: +237...)")
        return value


class ZoneSerializer(serializers.ModelSerializer):
    """Serializer pour les zones géographiques"""
    manager_nom = serializers.CharField(source='manager.get_full_name', read_only=True)
    surface_km2 = serializers.FloatField(read_only=True)
    nombre_commerciaux = serializers.SerializerMethodField()

    class Meta:
        model = Zone
        fields = [
            'id', 'nom', 'description', 'polygone', 'manager', 'manager_nom',
            'ville', 'pays', 'is_active', 'surface_km2', 'nombre_commerciaux',
            'created_at', 'updated_at',
        ]

    def get_nombre_commerciaux(self, obj):
        return obj.commerciaux.filter(statut='ACTIF').count()

    def validate_polygone(self, value):
        """Validation du polygone GeoJSON"""
        if value and value.num_coords < 4:
            raise serializers.ValidationError("Un polygone doit avoir au moins 3 points (plus le point de fermeture).")
        return value


class ProduitSerializer(serializers.ModelSerializer):
    """Serializer pour le catalogue produits"""
    categorie_display = serializers.CharField(source='get_categorie_display', read_only=True)

    class Meta:
        model = Produit
        fields = [
            'id', 'reference', 'nom', 'description', 'categorie', 'categorie_display',
            'prix_unitaire', 'prix_gros', 'stock', 'is_active', 'image',
            'created_at',
        ]


class ZoneAssigneeSerializer(serializers.ModelSerializer):
    commercial_nom = serializers.CharField(source='commercial.nom_complet', read_only=True)

    class Meta:
        model = ZoneAssignee
        fields = [
            'id', 'commercial', 'commercial_nom', 'manager', 'nom', 'polygone',
            'date_debut', 'date_fin', 'active', 'created_at',
        ]


class ObjectifSerializer(serializers.ModelSerializer):
    periode_display = serializers.CharField(source='get_periode_display', read_only=True)
    taux_realisation = serializers.FloatField(read_only=True)
    commercial_nom = serializers.CharField(source='commercial.nom_complet', read_only=True)

    class Meta:
        model = ObjectifCommercial
        fields = [
            'id', 'commercial', 'commercial_nom', 'periode', 'periode_display',
            'annee', 'mois', 'trimestre', 'cible', 'realise',
            'date_debut', 'date_fin', 'taux_realisation', 'is_atteint', 'created_at',
        ]


class CommercialListSerializer(serializers.ModelSerializer):
    """Serializer liste (light) pour les commerciaux"""
    nom_complet = serializers.CharField(read_only=True)   # ← CORRIGÉ
    email = serializers.CharField(source='user.email', read_only=True)
    telephones = TelephoneSerializer(many=True, read_only=True)
    manager_nom = serializers.SerializerMethodField()
    zone_active_nom = serializers.SerializerMethodField()
    statut_display = serializers.CharField(source='get_statut_display', read_only=True)
    taux_objectif = serializers.FloatField(read_only=True)
    distance_jour = serializers.FloatField(source='distance_totale_jour', read_only=True)
    nombre_visites_mois = serializers.SerializerMethodField()

    class Meta:
        model = Commercial
        fields = [
            'id', 'matricule', 'nom_complet', 'email', 'telephones',
            'statut', 'statut_display', 'manager', 'manager_nom', 'zone_active_nom',
            'taux_objectif', 'date_embauche', 'vehicule', 'immatriculation',
            'distance_jour', 'nombre_visites_mois',
            'created_at', 'updated_at',
        ]

    def get_manager_nom(self, obj):
        return obj.manager.get_full_name() if obj.manager else None

    def get_zone_active_nom(self, obj):
        za = obj.zone_active
        return za.nom if za else None

    def get_nombre_visites_mois(self, obj):
        from django.utils import timezone
        from apps.visites.models import Visite
        now = timezone.now()
        return Visite.objects.filter(
            commercial=obj,
            date_prevue__month=now.month,
            date_prevue__year=now.year,
            statut='EFFECTUEE'
        ).count()


class CommercialDetailSerializer(serializers.ModelSerializer):
    """Serializer détail (complet) pour un commercial"""
    user = serializers.SerializerMethodField()
    nom_complet = serializers.CharField(read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    telephones = TelephoneSerializer(many=True, read_only=True)
    manager_nom = serializers.SerializerMethodField()
    zones_assignees = ZoneAssigneeSerializer(many=True, read_only=True)
    statut_display = serializers.CharField(source='get_statut_display', read_only=True)
    objectifs = ObjectifSerializer(many=True, read_only=True)
    taux_objectif = serializers.FloatField(read_only=True)
    distance_jour = serializers.FloatField(source='distance_totale_jour', read_only=True)

    class Meta:
        model = Commercial
        fields = [
            'id', 'matricule', 'nom_complet', 'email', 'user', 'statut', 'statut_display',
            'manager', 'manager_nom', 'zones_assignees', 'objectifs', 'taux_objectif',
            'date_embauche', 'derniere_visite', 'total_ventes',
            'vehicule', 'immatriculation', 'telephones', 'distance_jour',
            'created_at', 'updated_at', 'created_by',
        ]

    def get_manager_nom(self, obj):
        return obj.manager.get_full_name() if obj.manager else None

    def get_user(self, obj):
        return {
            'id': obj.user.id,
            'email': obj.user.email,
            'first_name': obj.user.first_name,
            'last_name': obj.user.last_name,
            'photo': obj.user.photo.url if obj.user.photo else None,
            'role': obj.user.role,
        }


class CommercialCreateSerializer(serializers.ModelSerializer):
    """Serializer pour créer un commercial avec son user"""
    user_id = serializers.IntegerField(write_only=True, required=False)
    first_name = serializers.CharField(write_only=True, required=False)
    last_name = serializers.CharField(write_only=True, required=False)
    email = serializers.EmailField(write_only=True, required=False)
    password = serializers.CharField(write_only=True, required=False, min_length=8)
    phone = serializers.CharField(write_only=True, required=False, allow_blank=True)
    manager = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role='MANAGER'),
        write_only=True,
        required=False,
        allow_null=True,
    )
    telephones = TelephoneSerializer(many=True, required=False)

    class Meta:
        model = Commercial
        fields = [
            'user_id', 'first_name', 'last_name', 'email', 'password', 'phone', 'manager',
            'matricule', 'statut', 'date_embauche', 'vehicule', 'immatriculation', 'telephones',
        ]

    def validate(self, attrs):
        if attrs.get('user_id'):
            return attrs

        required = ['first_name', 'last_name', 'email', 'password']
        missing = [field for field in required if not attrs.get(field)]
        if missing:
            raise serializers.ValidationError({
                field: "Ce champ est requis pour creer un nouvel utilisateur."
                for field in missing
            })

        email = attrs['email'].lower().strip()
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({'email': "Cet email est deja utilise."})
        attrs['email'] = email
        return attrs

    def validate_user_id(self, value):
        try:
            user = User.objects.get(id=value, role='COMMERCIAL')
        except User.DoesNotExist:
            raise serializers.ValidationError("Utilisateur non trouvé ou n'est pas un commercial.")
        # Vérifier qu'il n'a pas déjà un profil commercial
        if hasattr(user, 'commercial_profile'):
            raise serializers.ValidationError("Cet utilisateur a déjà un profil commercial.")
        return value

    def create(self, validated_data):
        telephones_data = validated_data.pop('telephones', [])
        user_id = validated_data.pop('user_id', None)
        if user_id:
            user = User.objects.get(id=user_id)
        else:
            password = validated_data.pop('password')
            email = validated_data.pop('email')
            first_name = validated_data.pop('first_name')
            last_name = validated_data.pop('last_name')
            phone = validated_data.pop('phone', '')
            manager = validated_data.pop('manager', None)
            user = User.objects.create(
                username=email,
                email=email,
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                manager=manager,
                role='COMMERCIAL',
            )
            user.set_password(password)
            user.save()

        commercial = Commercial.objects.create(user=user, **validated_data)

        for tel_data in telephones_data:
            Telephone.objects.create(commercial=commercial, **tel_data)

        return commercial

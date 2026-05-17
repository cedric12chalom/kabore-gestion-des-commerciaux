"""
Modèles : Commercial, Téléphone, Zone géographique, Objectif, Produit
"""
import uuid
from django.db import models
from django.core.validators import RegexValidator, MinValueValidator
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from apps.core.gis import gis_models


class Telephone(models.Model):
    """Téléphone associé à un commercial (relation 1:N)"""

    class Type(models.TextChoices):
        MOBILE = 'MOBILE', _('Mobile')
        FIXE = 'FIXE', _('Fixe')
        TRAVAIL = 'TRAVAIL', _('Travail')
        WHATSAPP = 'WHATSAPP', _('WhatsApp')

    commercial = models.ForeignKey(
        'Commercial',
        on_delete=models.CASCADE,
        related_name='telephones',
        verbose_name=_('commercial'),
    )
    numero = models.CharField(
        _('numéro'),
        max_length=20,
        validators=[RegexValidator(
            regex=r'^\+[0-9]{1,4}[0-9\s\-\(\)]{6,20}$',
            message=_('Format international requis. Ex: +237 6XX XXX XXX')
        )]
    )
    type = models.CharField(
        _('type'),
        max_length=20,
        choices=Type.choices,
        default=Type.MOBILE,
    )
    is_principal = models.BooleanField(_('numéro principal'), default=False)
    is_whatsapp = models.BooleanField(_('WhatsApp disponible'), default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Téléphone')
        verbose_name_plural = _('Téléphones')
        unique_together = [['commercial', 'numero']]
        ordering = ['-is_principal', 'type']

    def __str__(self):
        return f"{self.numero} ({self.get_type_display()})"

    def save(self, *args, **kwargs):
        # Normaliser le numéro
        self.numero = self.numero.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
        super().save(*args, **kwargs)


class Zone(models.Model):
    """Zone géographique assignée (polygone PostGIS)"""

    nom = models.CharField(_('nom'), max_length=100, db_index=True)
    description = models.TextField(_('description'), blank=True)
    # Polygone géographique (coordonnées GPS)
    polygone = gis_models.PolygonField(
        _('zone géographique'),
        srid=4326,  # WGS84 - standard GPS
        geography=True,  # Calculs en mètres
        null=True,
        blank=True,
    )
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='zones_managed',
        limit_choices_to={'role': 'MANAGER'},
        verbose_name=_('manager responsable'),
    )
    ville = models.CharField(_('ville principale'), max_length=100, blank=True)
    pays = models.CharField(_('pays'), max_length=100, default='Cameroun')
    is_active = models.BooleanField(_('active'), default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Zone')
        verbose_name_plural = _('Zones')
        ordering = ['nom']

    def __str__(self):
        return f"{self.nom} ({self.ville})"

    @property
    def surface_km2(self):
        """Surface de la zone en km²"""
        if self.polygone:
            return self.polygone.area / 1_000_000  # m² → km²
        return 0


class Commercial(models.Model):
    """
    Profil commercial étendu.
    Lié 1:1 avec User via OneToOneField.
    """

    class Statut(models.TextChoices):
        ACTIF = 'ACTIF', _('Actif')
        CONGE = 'CONGE', _('En congé')
        SUSPENDU = 'SUSPENDU', _('Suspendu')
        INACTIF = 'INACTIF', _('Inactif')

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='commercial_profile',
        verbose_name=_('utilisateur'),
    )

    # Informations professionnelles
    matricule = models.CharField(
        _('matricule'),
        max_length=50,
        unique=True,
        db_index=True,
        default=lambda: f"COM-{uuid.uuid4().hex[:8].upper()}"
    )
    statut = models.CharField(
        _('statut'),
        max_length=20,
        choices=Statut.choices,
        default=Statut.ACTIF,
        db_index=True,
    )

    # Géolocalisation
    zone = models.ForeignKey(
        Zone,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='commerciaux',
        verbose_name=_('zone assignée'),
    )

    # Objectifs
    objectif_mensuel = models.DecimalField(
        _('objectif mensuel (FCFA)'),
        max_digits=15,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    objectif_trimestriel = models.DecimalField(
        _('objectif trimestriel (FCFA)'),
        max_digits=15,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )

    # Performance
    date_embauche = models.DateField(_("date d'embauche"), null=True, blank=True)
    derniere_visite = models.DateTimeField(_('dernière visite'), null=True, blank=True)
    total_ventes = models.DecimalField(
        _('total ventes cumulées'),
        max_digits=15,
        decimal_places=2,
        default=0,
    )

    # Préférences
    vehicule = models.CharField(_('véhicule'), max_length=100, blank=True)
    immatriculation = models.CharField(_('immatriculation'), max_length=50, blank=True)

    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='commerciaux_crees',
    )

    class Meta:
        verbose_name = _('Commercial')
        verbose_name_plural = _('Commerciaux')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['statut', 'zone']),
            models.Index(fields=['user', 'statut']),
        ]

    def __str__(self):
        return f"{self.user.get_full_name()} [{self.matricule}]"

    @property
    def nom_complet(self):
        return self.user.get_full_name()

    @property
    def email(self):
        return self.user.email

    @property
    def taux_objectif_mensuel(self):
        """Pourcentage d'atteinte de l'objectif mensuel"""
        from apps.commandes.models import Commande
        from django.utils import timezone
        import calendar

        now = timezone.now()
        debut_mois = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        fin_mois = now.replace(
            day=calendar.monthrange(now.year, now.month)[1],
            hour=23, minute=59, second=59
        )

        ca_mois = Commande.objects.filter(
            commercial=self,
            date__range=(debut_mois, fin_mois),
            statut__in=['VALIDEE', 'LIVREE']
        ).aggregate(total=models.Sum('montant_total'))['total'] or 0

        if self.objectif_mensuel > 0:
            return round((ca_mois / self.objectif_mensuel) * 100, 2)
        return 0

    @property
    def distance_totale_jour(self):
        """Distance totale parcourue aujourd'hui (km)"""
        from apps.gps.models import PositionGPS
        from django.utils import timezone

        today = timezone.now().date()
        positions = PositionGPS.objects.filter(
            commercial=self,
            timestamp__date=today
        ).order_by('timestamp')

        if positions.count() < 2:
            return 0

        total = 0
        for i in range(1, positions.count()):
            total += positions[i-1].position.distance(positions[i].position)

        return round(total / 1000, 2)  # m → km


class ObjectifCommercial(models.Model):
    """Objectifs de vente assignés à un commercial"""

    class Periode(models.TextChoices):
        MENSUEL = 'MENSUEL', _('Mensuel')
        TRIMESTRIEL = 'TRIMESTRIEL', _('Trimestriel')
        ANNUEL = 'ANNUEL', _('Annuel')

    commercial = models.ForeignKey(
        Commercial,
        on_delete=models.CASCADE,
        related_name='objectifs',
        verbose_name=_('commercial'),
    )
    periode = models.CharField(_('période'), max_length=20, choices=Periode.choices)
    montant_cible = models.DecimalField(
        _('montant cible'),
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(1)],
    )
    nombre_visites_cible = models.PositiveIntegerField(_('visites cibles'), default=0)
    nombre_clients_cible = models.PositiveIntegerField(_('clients cibles'), default=0)

    date_debut = models.DateField(_('date début'))
    date_fin = models.DateField(_('date fin'))

    montant_atteint = models.DecimalField(
        _('montant atteint'),
        max_digits=15,
        decimal_places=2,
        default=0,
    )
    nombre_visites_atteint = models.PositiveIntegerField(_('visites atteintes'), default=0)
    nombre_clients_atteint = models.PositiveIntegerField(_('clients atteints'), default=0)

    is_atteint = models.BooleanField(_('objectif atteint'), default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Objectif Commercial')
        verbose_name_plural = _('Objectifs Commerciaux')
        ordering = ['-date_debut']
        unique_together = [['commercial', 'periode', 'date_debut']]

    def __str__(self):
        return f"Objectif {self.periode} - {self.commercial.nom_complet}"

    @property
    def taux_realisation(self):
        if self.montant_cible > 0:
            return round((self.montant_atteint / self.montant_cible) * 100, 2)
        return 0

    def save(self, *args, **kwargs):
        self.is_atteint = self.taux_realisation >= 100
        super().save(*args, **kwargs)


class Produit(models.Model):
    """Catalogue produits/services"""

    class Categorie(models.TextChoices):
        ELECTRONIQUE = 'ELECTRONIQUE', _('Électronique')
        ALIMENTAIRE = 'ALIMENTAIRE', _('Alimentaire')
        TEXTILE = 'TEXTILE', _('Textile')
        SERVICES = 'SERVICES', _('Services')
        AUTRE = 'AUTRE', _('Autre')

    reference = models.CharField(_('référence'), max_length=50, unique=True, db_index=True)
    nom = models.CharField(_('nom'), max_length=200, db_index=True)
    description = models.TextField(_('description'), blank=True)
    categorie = models.CharField(_('catégorie'), max_length=20, choices=Categorie.choices)
    prix_unitaire = models.DecimalField(_('prix unitaire'), max_digits=12, decimal_places=2)
    prix_gros = models.DecimalField(_('prix gros'), max_digits=12, decimal_places=2, null=True, blank=True)
    stock = models.PositiveIntegerField(_('stock'), default=0)
    is_active = models.BooleanField(_('actif'), default=True)
    image = models.ImageField(_('image'), upload_to='produits/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Produit')
        verbose_name_plural = _('Produits')
        ordering = ['nom']

    def __str__(self):
        return f"{self.reference} - {self.nom}"

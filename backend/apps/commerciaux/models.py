"""
Modèles : Commercial, Téléphone, Zone géographique, Objectif, Produit
"""
import uuid
from django.db import OperationalError, ProgrammingError, models
from django.core.validators import RegexValidator, MinValueValidator
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from apps.core.gis import distance_m, gis_models


def generate_matricule():
    return f"COM-{uuid.uuid4().hex[:8].upper()}"


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


class ZoneAssignee(models.Model):
    """Zone assignée à un commercial par son manager (polygone PostGIS)."""

    commercial = models.ForeignKey(
        'Commercial',
        on_delete=models.CASCADE,
        related_name='zones_assignees',
        verbose_name=_('commercial'),
    )
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='zones_assignees',
        limit_choices_to={'role': 'MANAGER'},
        verbose_name=_('manager'),
    )
    nom = models.CharField(_('nom'), max_length=100, default='Zone')
    polygone = gis_models.PolygonField(
        _('zone géographique'),
        srid=4326,
        geography=True,
    )
    date_debut = models.DateField(_('date début'))
    date_fin = models.DateField(_('date fin'), null=True, blank=True)
    active = models.BooleanField(_('active'), default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Zone assignée')
        verbose_name_plural = _('Zones assignées')
        ordering = ['-date_debut']

    def __str__(self):
        return f"{self.nom} → {self.commercial}"

    def save(self, *args, **kwargs):
        if self.active:
            ZoneAssignee.objects.filter(
                commercial=self.commercial, active=True
            ).exclude(pk=self.pk).update(active=False)
        super().save(*args, **kwargs)


class Zone(models.Model):
    """Zone géographique (legacy — préférer ZoneAssignee)."""

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
        default=generate_matricule,
    )
    statut = models.CharField(
        _('statut'),
        max_length=20,
        choices=Statut.choices,
        default=Statut.ACTIF,
        db_index=True,
    )

    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='equipe_commerciaux',
        limit_choices_to={'role': 'MANAGER'},
        verbose_name=_('manager responsable'),
        null=True,
        blank=True,
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
            models.Index(fields=['statut', 'manager']),
            models.Index(fields=['user', 'statut']),
        ]

    @property
    def zone_active(self):
        return self.zones_assignees.filter(active=True).first()

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
        from django.utils import timezone
        now = timezone.now()
        obj = self.objectifs.filter(
            periode=ObjectifCommercial.Periode.MENSUEL,
            annee=now.year,
            mois=now.month,
        ).first()
        return obj.taux_realisation if obj else 0

    @property
    def distance_totale_jour(self):
        from apps.gps.models import HistoriqueParcours
        from django.utils import timezone

        today = timezone.now().date()
        try:
            positions = list(HistoriqueParcours.objects.filter(
                commercial=self,
                timestamp__date=today,
            ).order_by('timestamp'))
        except (OperationalError, ProgrammingError):
            return 0

        if len(positions) < 2:
            return 0

        total = 0
        for i in range(1, len(positions)):
            step = distance_m(positions[i - 1].position, positions[i].position)
            if step is not None:
                total += step
        return round(total / 1000, 2)


class ObjectifCommercial(models.Model):
    """Objectifs de vente assignés à un commercial par le manager."""

    class Periode(models.TextChoices):
        MENSUEL = 'MENSUEL', _('Mensuel')
        TRIMESTRIEL = 'TRIMESTRIEL', _('Trimestriel')

    commercial = models.ForeignKey(
        Commercial,
        on_delete=models.CASCADE,
        related_name='objectifs',
        verbose_name=_('commercial'),
    )
    periode = models.CharField(_('période'), max_length=20, choices=Periode.choices)
    annee = models.PositiveIntegerField(_('année'), default=2026)
    mois = models.PositiveSmallIntegerField(_('mois'), null=True, blank=True)
    trimestre = models.PositiveSmallIntegerField(_('trimestre'), null=True, blank=True)
    cible = models.DecimalField(
        _('montant cible'),
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(1)],
    )
    realise = models.DecimalField(
        _('montant réalisé'),
        max_digits=15,
        decimal_places=2,
        default=0,
    )
    date_debut = models.DateField(_('date début'), null=True, blank=True)
    date_fin = models.DateField(_('date fin'), null=True, blank=True)
    is_atteint = models.BooleanField(_('objectif atteint'), default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Objectif Commercial')
        verbose_name_plural = _('Objectifs Commerciaux')
        ordering = ['-annee', '-mois']
        unique_together = [['commercial', 'periode', 'annee', 'mois', 'trimestre']]

    @property
    def montant_cible(self):
        return self.cible

    @property
    def montant_atteint(self):
        return self.realise

    def __str__(self):
        return f"Objectif {self.periode} - {self.commercial.nom_complet}"

    @property
    def taux_realisation(self):
        if self.cible > 0:
            return round((float(self.realise) / float(self.cible)) * 100, 2)
        return 0

    def incrementer_realise(self, montant):
        from decimal import Decimal
        self.realise += Decimal(str(montant))
        self.is_atteint = self.taux_realisation >= 100
        self.save(update_fields=['realise', 'is_atteint'])

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

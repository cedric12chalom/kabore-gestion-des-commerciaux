"""
Modèles : Visite, Compte-rendu, Check-in/Check-out GPS
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from apps.core.gis import gis_models


class Visite(models.Model):
    """Visite client planifiée ou effectuée"""

    class Statut(models.TextChoices):
        PLANIFIEE = 'PLANIFIEE', _('Planifiée')
        EN_COURS = 'EN_COURS', _('En cours')
        EFFECTUEE = 'EFFECTUEE', _('Effectuée')
        REPORTEE = 'REPORTEE', _('Reportée')
        ANNULEE = 'ANNULEE', _('Annulée')

    class Type(models.TextChoices):
        VISITE_REGULIERE = 'REGULIERE', _('Visite régulière')
        RECOUVREMENT = 'RECOUVREMENT', _('Recouvrement')
        LIVRAISON = 'LIVRAISON', _('Livraison')
        PRESENTATION = 'PRESENTATION', _('Présentation produit')
        AUTRE = 'AUTRE', _('Autre')

    # Relations
    commercial = models.ForeignKey(
        'commerciaux.Commercial',
        on_delete=models.CASCADE,
        related_name='visites',
        verbose_name=_('commercial'),
    )
    client = models.ForeignKey(
        'clients.Client',
        on_delete=models.CASCADE,
        related_name='visites',
        verbose_name=_('client'),
    )

    # Planification
    type_visite = models.CharField(_('type'), max_length=20, choices=Type.choices, default=Type.VISITE_REGULIERE)
    date_prevue = models.DateTimeField(_('date prévue'))
    date_effective = models.DateTimeField(_('date effective'), null=True, blank=True)
    duree_estimee = models.PositiveIntegerField(_('durée estimée (min)'), default=30)
    objectif = models.TextField(_('objectif de la visite'), blank=True)

    # Statut
    statut = models.CharField(_('statut'), max_length=20, choices=Statut.choices, default=Statut.PLANIFIEE, db_index=True)

    # Check-in GPS
    checkin_lat = models.DecimalField(_('check-in latitude'), max_digits=10, decimal_places=8, null=True, blank=True)
    checkin_lng = models.DecimalField(_('check-in longitude'), max_digits=11, decimal_places=8, null=True, blank=True)
    checkin_position = gis_models.PointField(_('position check-in'), srid=4326, geography=True, null=True, blank=True)
    checkin_timestamp = models.DateTimeField(_('heure check-in'), null=True, blank=True)

    # Check-out GPS
    checkout_lat = models.DecimalField(_('check-out latitude'), max_digits=10, decimal_places=8, null=True, blank=True)
    checkout_lng = models.DecimalField(_('check-out longitude'), max_digits=11, decimal_places=8, null=True, blank=True)
    checkout_position = gis_models.PointField(_('position check-out'), srid=4326, geography=True, null=True, blank=True)
    checkout_timestamp = models.DateTimeField(_('heure check-out'), null=True, blank=True)

    # Compte-rendu
    duree_reelle = models.PositiveIntegerField(_('durée réelle (min)'), null=True, blank=True)
    compte_rendu = models.TextField(_('compte-rendu'), blank=True)
    actions_suivantes = models.TextField(_('actions suivantes'), blank=True)
    satisfaction_client = models.PositiveSmallIntegerField(
        _('satisfaction client'),
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True,
    )

    # Commande liée (optionnel)
    commande = models.OneToOneField(
        'commandes.Commande',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='visite',
        verbose_name=_('commande associée'),
    )

    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Visite')
        verbose_name_plural = _('Visites')
        ordering = ['-date_prevue']
        indexes = [
            models.Index(fields=['commercial', 'statut', 'date_prevue']),
            models.Index(fields=['client', 'date_prevue']),
            models.Index(fields=['statut', 'date_prevue']),
        ]

    def __str__(self):
        return f"Visite {self.client.raison_sociale} - {self.date_prevue.strftime('%d/%m/%Y')}"

    @property
    def is_validee(self):
        """Une visite est validée si elle a un check-in GPS"""
        return self.checkin_position is not None and self.statut == self.Statut.EFFECTUEE

    @property
    def distance_checkin_client(self):
        """Distance entre le check-in et la position du client (mètres)"""
        if self.checkin_position and self.client.position:
            return self.checkin_position.distance(self.client.position)
        return None


class RapportVisite(models.Model):
    """Rapport détaillé post-visite"""

    visite = models.OneToOneField(
        Visite,
        on_delete=models.CASCADE,
        related_name='rapport',
        verbose_name=_('visite'),
    )

    # Détails commerciaux
    produits_presentes = models.ManyToManyField(
        'commerciaux.Produit',
        blank=True,
        related_name='rapports',
        verbose_name=_('produits présentés'),
    )
    echantillons_distribues = models.PositiveIntegerField(_('échantillons distribués'), default=0)

    # Feedback
    besoins_client = models.TextField(_('besoins identifiés'), blank=True)
    obstacles = models.TextField(_('obstacles rencontrés'), blank=True)
    prochaine_action = models.CharField(_('prochaine action'), max_length=200, blank=True)
    date_prochaine_visite = models.DateTimeField(_('date prochaine visite'), null=True, blank=True)

    # Photo
    photo = models.ImageField(_('photo'), upload_to='visites/photos/', blank=True, null=True)
    signature = models.TextField(_('signature électronique'), blank=True)  # Base64

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Rapport de Visite')
        verbose_name_plural = _('Rapports de Visite')

    def __str__(self):
        return f"Rapport - {self.visite}"

"""
Modèles : Visite, Compte-rendu, Check-in/Check-out GPS
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from apps.core.gis import distance_m, gis_models


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
    contact_nom = models.CharField(_('nom du contact'), max_length=200, default='')
    contact_telephone = models.CharField(_('téléphone'), max_length=30, blank=True)
    quartier = models.CharField(_('quartier'), max_length=100, blank=True)
    adresse_complete = models.TextField(_('adresse'), blank=True)

    # Planification
    type_visite = models.CharField(_('type'), max_length=20, choices=Type.choices, default=Type.VISITE_REGULIERE)
    date_prevue = models.DateTimeField(_('date prévue'))
    date_effective = models.DateTimeField(_('date effective'), null=True, blank=True)
    duree_estimee = models.PositiveIntegerField(_('durée estimée (min)'), default=30)
    objectif = models.TextField(_('objectif de la visite'), blank=True)

    # Statut
    statut = models.CharField(_('statut'), max_length=20, choices=Statut.choices, default=Statut.PLANIFIEE, db_index=True)

    # GPS auto (capturé depuis PositionTempsReel au check-in/out)
    checkin_position = gis_models.PointField(_('position check-in'), srid=4326, geography=True, null=True, blank=True)
    checkin_timestamp = models.DateTimeField(_('heure check-in'), null=True, blank=True)
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
            models.Index(fields=['contact_nom', 'date_prevue']),
            models.Index(fields=['statut', 'date_prevue']),
        ]

    def __str__(self):
        return f"Visite {self.contact_nom} - {self.date_prevue.strftime('%d/%m/%Y')}"

    @property
    def is_validee(self):
        return self.checkin_position is not None and self.statut == self.Statut.EFFECTUEE


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

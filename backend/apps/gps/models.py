"""
Modèles : PositionGPS, HistoriqueParcours, AlerteZone
Tracking GPS temps réel avec PostGIS
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from apps.core.gis import gis_models, Point


class PositionGPS(models.Model):
    """
    Position GPS enregistrée toutes les 30 secondes.
    Utilise PostGIS PointField pour les requêtes spatiales.
    """

    commercial = models.ForeignKey(
        'commerciaux.Commercial',
        on_delete=models.CASCADE,
        related_name='positions',
        verbose_name=_('commercial'),
        db_index=True,
    )

    # Coordonnées GPS
    position = gis_models.PointField(
        _('position GPS'),
        srid=4326,
        geography=True,
        db_index=True,
    )
    latitude = models.DecimalField(_('latitude'), max_digits=10, decimal_places=8, db_index=True)
    longitude = models.DecimalField(_('longitude'), max_digits=11, decimal_places=8, db_index=True)

    # Métadonnées GPS
    precision = models.FloatField(_('précision (m)'), null=True, blank=True, validators=[MinValueValidator(0)])
    altitude = models.FloatField(_('altitude (m)'), null=True, blank=True)
    vitesse = models.FloatField(_('vitesse (km/h)'), null=True, blank=True, validators=[MinValueValidator(0)])
    cap = models.FloatField(_('cap (degrés)'), null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(360)])

    # Source
    source = models.CharField(_('source'), max_length=20, default='GPS', choices=[
        ('GPS', 'GPS'),
        ('NETWORK', 'Réseau'),
        ('MANUAL', 'Manuel'),
    ])

    # Timestamp
    timestamp = models.DateTimeField(_('horodatage'), auto_now_add=True, db_index=True)

    # Mode hors-ligne
    is_sync = models.BooleanField(_('synchronisé'), default=True)
    date_enregistrement_local = models.DateTimeField(_('date enregistrement local'), null=True, blank=True)

    class Meta:
        verbose_name = _('Position GPS')
        verbose_name_plural = _('Positions GPS')
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['commercial', 'timestamp']),
            models.Index(fields=['commercial', '-timestamp']),
            models.Index(fields=['timestamp', 'is_sync']),
        ]

    def __str__(self):
        return f"{self.commercial.nom_complet} - {self.latitude}, {self.longitude} @ {self.timestamp.strftime('%H:%M:%S')}"

    def save(self, *args, **kwargs):
        # Synchroniser PointField avec lat/lng
        if self.latitude and self.longitude and not self.position:
            self.position = str(Point(float(self.longitude), float(self.latitude)))
        elif settings.USE_GIS and self.position and not self.latitude:
            self.longitude = self.position.x
            self.latitude = self.position.y
        super().save(*args, **kwargs)


class HistoriqueParcours(models.Model):
    """
    Résumé journalier du parcours d'un commercial.
    Agrégation des positions pour performance.
    """

    commercial = models.ForeignKey(
        'commerciaux.Commercial',
        on_delete=models.CASCADE,
        related_name='parcours',
        verbose_name=_('commercial'),
    )

    date = models.DateField(_('date'), db_index=True)

    # Statistiques
    distance_totale_km = models.DecimalField(_('distance totale (km)'), max_digits=10, decimal_places=2, default=0)
    duree_totale_minutes = models.PositiveIntegerField(_('durée totale (min)'), default=0)
    vitesse_moyenne_kmh = models.DecimalField(_('vitesse moyenne (km/h)'), max_digits=5, decimal_places=2, default=0)
    nombre_positions = models.PositiveIntegerField(_('nombre de positions'), default=0)

    # Zone
    zone_visites = models.ManyToManyField(
        'commerciaux.Zone',
        blank=True,
        related_name='parcours',
        verbose_name=_('zones visitées'),
    )

    # Géométrie du parcours (LineString PostGIS)
    trajectoire = gis_models.LineStringField(
        _('trajectoire'),
        srid=4326,
        geography=True,
        null=True,
        blank=True,
    )

    # Première et dernière position
    premiere_position = gis_models.PointField(_('première position'), srid=4326, geography=True, null=True)
    derniere_position = gis_models.PointField(_('dernière position'), srid=4326, geography=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Historique de Parcours')
        verbose_name_plural = _('Historiques de Parcours')
        ordering = ['-date']
        unique_together = [['commercial', 'date']]

    def __str__(self):
        return f"Parcours {self.commercial.nom_complet} - {self.date}"


class AlerteZone(models.Model):
    """Alerte lorsqu'un commercial sort de sa zone assignée"""

    class Type(models.TextChoices):
        SORTIE_ZONE = 'SORTIE', _('Sortie de zone')
        ENTREE_ZONE = 'ENTREE', _('Entrée dans zone')
        INACTIVITE = 'INACTIVITE', _('Inactivité prolongée'),

    class Statut(models.TextChoices):
        NOUVELLE = 'NOUVELLE', _('Nouvelle')
        LUE = 'LUE', _('Lue')
        TRAITEE = 'TRAITEE', _('Traitée'),

    commercial = models.ForeignKey(
        'commerciaux.Commercial',
        on_delete=models.CASCADE,
        related_name='alertes',
        verbose_name=_('commercial'),
    )
    zone = models.ForeignKey(
        'commerciaux.Zone',
        on_delete=models.CASCADE,
        related_name='alertes',
        verbose_name=_('zone concernée'),
    )

    type_alerte = models.CharField(_('type'), max_length=20, choices=Type.choices)
    statut = models.CharField(_('statut'), max_length=20, choices=Statut.choices, default=Statut.NOUVELLE)

    # Position au moment de l'alerte
    position = gis_models.PointField(_('position'), srid=4326, geography=True)
    distance_zone_m = models.FloatField(_('distance de la zone (m)'), null=True, blank=True)

    # Détails
    message = models.TextField(_('message'), blank=True)
    timestamp = models.DateTimeField(_('horodatage'), auto_now_add=True)

    # Traitement
    traite_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='alertes_traitees',
        verbose_name=_('traité par'),
    )
    date_traitement = models.DateTimeField(_('date traitement'), null=True, blank=True)

    class Meta:
        verbose_name = _('Alerte Zone')
        verbose_name_plural = _('Alertes Zones')
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.get_type_alerte_display()} - {self.commercial.nom_complet}"

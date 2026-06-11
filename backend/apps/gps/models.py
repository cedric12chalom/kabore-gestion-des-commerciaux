"""
Modèles GPS temps réel — PositionTempsReel + HistoriqueParcours
La géolocalisation est automatique via WebSocket (aucune saisie manuelle).
"""
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from apps.core.gis import gis_models, Point


class PositionTempsReel(models.Model):
    """Position actuelle d'un commercial (OneToOne)."""

    commercial = models.OneToOneField(
        'commerciaux.Commercial',
        on_delete=models.CASCADE,
        related_name='position_actuelle',
        verbose_name=_('commercial'),
    )
    position = gis_models.PointField(_('position GPS'), srid=4326, geography=True)
    precision = models.FloatField(_('précision (m)'), null=True, blank=True)
    vitesse = models.FloatField(_('vitesse (km/h)'), null=True, blank=True)
    cap = models.FloatField(_('cap (degrés)'), null=True, blank=True)
    online = models.BooleanField(_('en ligne'), default=False, db_index=True)
    dernier_update = models.DateTimeField(_('dernière mise à jour'), db_index=True)

    class Meta:
        verbose_name = _('Position temps réel')
        verbose_name_plural = _('Positions temps réel')
        indexes = [models.Index(fields=['online', 'dernier_update'])]

    def __str__(self):
        status = 'online' if self.online else 'offline'
        return f"{self.commercial} — {status}"

    @property
    def latitude(self) -> float:
        from apps.core.gis import point_coords
        coords = point_coords(self.position)
        return coords[1] if coords else 0

    @property
    def longitude(self) -> float:
        from apps.core.gis import point_coords
        coords = point_coords(self.position)
        return coords[0] if coords else 0

    @classmethod
    def seuil_hors_ligne_secondes(cls) -> int:
        return 120

    def est_hors_ligne(self) -> bool:
        return (timezone.now() - self.dernier_update).total_seconds() > self.seuil_hors_ligne_secondes()

    @classmethod
    def upsert_from_payload(cls, commercial, payload: dict) -> 'PositionTempsReel':
        point = Point(float(payload['lng']), float(payload['lat']), srid=4326)
        obj, _ = cls.objects.update_or_create(
            commercial=commercial,
            defaults={
                'position': point,
                'precision': payload.get('accuracy'),
                'vitesse': payload.get('speed'),
                'cap': payload.get('heading'),
                'online': True,
                'dernier_update': timezone.now(),
            },
        )
        return obj


class HistoriqueParcours(models.Model):
    """Trace GPS point-par-point (rétention 30 jours)."""

    commercial = models.ForeignKey(
        'commerciaux.Commercial',
        on_delete=models.CASCADE,
        related_name='historique_positions',
        db_index=True,
    )
    position = gis_models.PointField(_('position'), srid=4326, geography=True)
    precision = models.FloatField(null=True, blank=True)
    vitesse = models.FloatField(null=True, blank=True)
    cap = models.FloatField(null=True, blank=True)
    timestamp = models.DateTimeField(_('horodatage'), db_index=True, default=timezone.now)

    class Meta:
        verbose_name = _('Historique parcours')
        verbose_name_plural = _('Historiques parcours')
        ordering = ['-timestamp']
        indexes = [models.Index(fields=['commercial', '-timestamp'])]

    def __str__(self):
        return f"{self.commercial} @ {self.timestamp:%Y-%m-%d %H:%M:%S}"

    @classmethod
    def creer_depuis_payload(cls, commercial, payload: dict) -> 'HistoriqueParcours':
        return cls.objects.create(
            commercial=commercial,
            position=Point(float(payload['lng']), float(payload['lat']), srid=4326),
            precision=payload.get('accuracy'),
            vitesse=payload.get('speed'),
            cap=payload.get('heading'),
            timestamp=timezone.now(),
        )

    @classmethod
    def purger_ancien(cls, jours: int = 30) -> int:
        seuil = timezone.now() - timezone.timedelta(days=jours)
        deleted, _ = cls.objects.filter(timestamp__lt=seuil).delete()
        return deleted


class AlerteZone(models.Model):
    """Alerte lorsqu'un commercial sort de sa zone assignée."""

    class Type(models.TextChoices):
        SORTIE_ZONE = 'SORTIE', _('Sortie de zone')
        ENTREE_ZONE = 'ENTREE', _('Entrée dans zone')
        INACTIVITE = 'INACTIVITE', _('Inactivité prolongée')

    class Statut(models.TextChoices):
        NOUVELLE = 'NOUVELLE', _('Nouvelle')
        LUE = 'LUE', _('Lue')
        TRAITEE = 'TRAITEE', _('Traitée')

    commercial = models.ForeignKey(
        'commerciaux.Commercial',
        on_delete=models.CASCADE,
        related_name='alertes',
    )
    zone_assignee = models.ForeignKey(
        'commerciaux.ZoneAssignee',
        on_delete=models.CASCADE,
        related_name='alertes',
        null=True,
        blank=True,
    )
    type_alerte = models.CharField(max_length=20, choices=Type.choices)
    statut = models.CharField(max_length=20, choices=Statut.choices, default=Statut.NOUVELLE)
    position = gis_models.PointField(srid=4326, geography=True)
    distance_zone_m = models.FloatField(null=True, blank=True)
    message = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    traite_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='alertes_traitees',
    )
    date_traitement = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']

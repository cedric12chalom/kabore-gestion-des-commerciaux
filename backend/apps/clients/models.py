"""
Modèles : Client, Adresse géocodée
"""
from django.db import models
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from apps.core.gis import gis_models


class Client(models.Model):
    """Client avec adresse géocodée (lat/lng)"""

    class Potentiel(models.TextChoices):
        A = 'A', _('A - Très fort')
        B = 'B', _('B - Fort')
        C = 'C', _('C - Moyen')
        D = 'D', _('D - Faible')

    class Secteur(models.TextChoices):
        RETAIL = 'RETAIL', _('Retail / Grande distribution')
        HORECA = 'HORECA', _('Hôtellerie / Restauration')
        SANTE = 'SANTE', _('Santé / Pharmaceutique')
        EDUCATION = 'EDUCATION', _('Éducation')
        INDUSTRIE = 'INDUSTRIE', _('Industrie')
        SERVICES = 'SERVICES', _('Services')
        AUTRE = 'AUTRE', _('Autre')

    # Identité
    raison_sociale = models.CharField(_('raison sociale'), max_length=200, db_index=True)
    nom_contact = models.CharField(_('nom du contact'), max_length=150, blank=True)
    email = models.EmailField(_('email'), blank=True)
    telephone = models.CharField(
        _('téléphone'),
        max_length=20,
        blank=True,
        validators=[RegexValidator(
            regex=r'^\+[0-9]{1,4}[0-9\s\-\(\)]{6,20}$',
            message=_('Format international requis.')
        )]
    )

    # Adresse géocodée
    adresse = models.CharField(_('adresse'), max_length=300)
    ville = models.CharField(_('ville'), max_length=100, db_index=True)
    code_postal = models.CharField(_('code postal'), max_length=20, blank=True)
    pays = models.CharField(_('pays'), max_length=100, default='Cameroun')

    # Coordonnées GPS (PointField PostGIS)
    position = gis_models.PointField(
        _('position GPS'),
        srid=4326,
        geography=True,
        null=True,
        blank=True,
    )

    # Métadonnées
    secteur = models.CharField(_('secteur'), max_length=20, choices=Secteur.choices, blank=True)
    potentiel = models.CharField(_('potentiel'), max_length=5, choices=Potentiel.choices, default=Potentiel.C)

    # Commercial référent
    commercial_referent = models.ForeignKey(
        'commerciaux.Commercial',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='clients',
        verbose_name=_('commercial référent'),
    )

    # Statut
    is_actif = models.BooleanField(_('client actif'), default=True, db_index=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    # Notes
    notes = models.TextField(_('notes'), blank=True)

    class Meta:
        verbose_name = _('Client')
        verbose_name_plural = _('Clients')
        ordering = ['-date_creation']
        indexes = [
            models.Index(fields=['ville', 'secteur']),
            models.Index(fields=['commercial_referent', 'is_actif']),
            models.Index(fields=['potentiel', 'is_actif']),
        ]

    def __str__(self):
        return f"{self.raison_sociale} ({self.ville})"

    @property
    def latitude(self):
        return self.position.y if self.position else None

    @property
    def longitude(self):
        return self.position.x if self.position else None

    @property
    def nombre_visites(self):
        return self.visites.count()

    @property
    def ca_total(self):
        from apps.commandes.models import Commande
        return Commande.objects.filter(
            client=self,
            statut__in=['VALIDEE', 'LIVREE']
        ).aggregate(total=models.Sum('montant_total'))['total'] or 0

    def save(self, *args, **kwargs):
        # Si position est fournie mais pas ville, on ne fait rien
        # Si ville est fournie mais pas position, on pourrait géocoder (optionnel)
        super().save(*args, **kwargs)

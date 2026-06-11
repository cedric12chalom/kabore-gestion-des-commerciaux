"""
Modèles : Commande, LigneCommande, Opportunité
Sans modèle Client — contact inline sur la commande.
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from apps.core.gis import gis_models


class Commande(models.Model):
    """Commande créée par Manager/Admin, livrée par le Commercial."""

    class Statut(models.TextChoices):
        EN_ATTENTE = 'EN_ATTENTE', _('En attente')
        EN_COURS = 'EN_COURS', _('En cours')
        LIVREE = 'LIVREE', _('Livrée')
        ANNULEE = 'ANNULEE', _('Annulée')

    reference = models.CharField(_('référence'), max_length=50, unique=True, db_index=True)
    commercial = models.ForeignKey(
        'commerciaux.Commercial',
        on_delete=models.CASCADE,
        related_name='commandes',
    )
    cree_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='commandes_creees',
    )

    # Contact inline (remplace Client)
    contact_nom = models.CharField(_('nom du contact'), max_length=200)
    contact_telephone = models.CharField(_('téléphone'), max_length=30)
    quartier = models.CharField(_('quartier'), max_length=100)
    adresse_complete = models.TextField(_('adresse complète'))

    date = models.DateTimeField(_('date de commande'), auto_now_add=True)
    date_livraison = models.DateTimeField(_('date livraison'), null=True, blank=True)
    montant_total = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    montant_remise = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    statut = models.CharField(
        max_length=20, choices=Statut.choices,
        default=Statut.EN_ATTENTE, db_index=True,
    )

    # GPS capturé auto à la livraison
    position_livraison = gis_models.PointField(
        srid=4326, geography=True, null=True, blank=True,
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']
        indexes = [
            models.Index(fields=['commercial', 'statut', 'date']),
            models.Index(fields=['statut', 'date']),
        ]

    def __str__(self):
        return f"CMD-{self.reference} - {self.contact_nom}"


class LigneCommande(models.Model):
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE, related_name='lignes')
    produit = models.ForeignKey('commerciaux.Produit', on_delete=models.PROTECT, related_name='lignes_commande')
    quantite = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    prix_unitaire = models.DecimalField(max_digits=12, decimal_places=2)
    remise = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    montant_ligne = models.DecimalField(max_digits=15, decimal_places=2)

    def save(self, *args, **kwargs):
        self.montant_ligne = (self.prix_unitaire * self.quantite) - self.remise
        super().save(*args, **kwargs)
        self.commande.montant_total = sum(l.montant_ligne for l in self.commande.lignes.all())
        self.commande.save(update_fields=['montant_total'])


class Opportunite(models.Model):
    class Etape(models.TextChoices):
        PROSPECT = 'PROSPECT', _('Prospect')
        QUALIFICATION = 'QUALIFICATION', _('Qualification')
        OFFRE = 'OFFRE', _('Offre envoyée')
        NEGOCIATION = 'NEGOCIATION', _('Négociation')
        GAGNE = 'GAGNE', _('Gagnée')
        PERDU = 'PERDU', _('Perdue')
        REPORTE = 'REPORTE', _('Reportée')

    titre = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    commercial = models.ForeignKey('commerciaux.Commercial', on_delete=models.CASCADE, related_name='opportunites')
    contact_nom = models.CharField(max_length=200, default='')
    contact_telephone = models.CharField(max_length=30, blank=True)
    etape = models.CharField(max_length=20, choices=Etape.choices, default=Etape.PROSPECT, db_index=True)
    probabilite = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)], default=20)
    montant_estime = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    montant_final = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_cloture_prevue = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    commande = models.OneToOneField(Commande, on_delete=models.SET_NULL, null=True, blank=True, related_name='opportunite')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date_creation']

    def __str__(self):
        return f"{self.titre} - {self.contact_nom}"

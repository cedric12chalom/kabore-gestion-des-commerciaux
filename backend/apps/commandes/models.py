"""
Modèles : Commande, LigneCommande, Opportunité
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _


class Commande(models.Model):
    """Commande passée par un commercial depuis le terrain"""

    class Statut(models.TextChoices):
        EN_ATTENTE = 'EN_ATTENTE', _('En attente')
        VALIDEE = 'VALIDEE', _('Validée')
        EN_PREPARATION = 'EN_PREPARATION', _('En préparation')
        EXPEDIEE = 'EXPEDIEE', _('Expédiée')
        LIVREE = 'LIVREE', _('Livrée')
        ANNULEE = 'ANNULEE', _('Annulée')
        REFUSEE = 'REFUSEE', _('Refusée')

    # Références
    reference = models.CharField(_('référence'), max_length=50, unique=True, db_index=True)

    # Relations
    commercial = models.ForeignKey(
        'commerciaux.Commercial',
        on_delete=models.CASCADE,
        related_name='commandes',
        verbose_name=_('commercial'),
    )
    client = models.ForeignKey(
        'clients.Client',
        on_delete=models.CASCADE,
        related_name='commandes',
        verbose_name=_('client'),
    )

    # Dates
    date = models.DateTimeField(_('date de commande'), auto_now_add=True)
    date_validation = models.DateTimeField(_('date validation'), null=True, blank=True)
    date_livraison_prevue = models.DateField(_('date livraison prévue'), null=True, blank=True)
    date_livraison_effective = models.DateField(_('date livraison effective'), null=True, blank=True)

    # Montants
    montant_total = models.DecimalField(_('montant total'), max_digits=15, decimal_places=2, default=0)
    montant_remise = models.DecimalField(_('remise totale'), max_digits=15, decimal_places=2, default=0)
    montant_ht = models.DecimalField(_('montant HT'), max_digits=15, decimal_places=2, default=0)
    tva = models.DecimalField(_('TVA'), max_digits=15, decimal_places=2, default=0)

    # Statut
    statut = models.CharField(_('statut'), max_length=20, choices=Statut.choices, default=Statut.EN_ATTENTE, db_index=True)

    # Livraison
    adresse_livraison = models.TextField(_('adresse de livraison'), blank=True)
    notes = models.TextField(_('notes'), blank=True)

    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Commande')
        verbose_name_plural = _('Commandes')
        ordering = ['-date']
        indexes = [
            models.Index(fields=['commercial', 'statut', 'date']),
            models.Index(fields=['client', 'statut']),
            models.Index(fields=['statut', 'date']),
        ]

    def __str__(self):
        return f"CMD-{self.reference} - {self.client.raison_sociale}"

    @property
    def nombre_articles(self):
        return self.lignes.count()

    @property
    def montant_ttc(self):
        return self.montant_ht + self.tva - self.montant_remise


class LigneCommande(models.Model):
    """Ligne de détail d'une commande"""

    commande = models.ForeignKey(
        Commande,
        on_delete=models.CASCADE,
        related_name='lignes',
        verbose_name=_('commande'),
    )
    produit = models.ForeignKey(
        'commerciaux.Produit',
        on_delete=models.PROTECT,
        related_name='lignes_commande',
        verbose_name=_('produit'),
    )
    quantite = models.PositiveIntegerField(_('quantité'), validators=[MinValueValidator(1)])
    prix_unitaire = models.DecimalField(_('prix unitaire'), max_digits=12, decimal_places=2)
    remise = models.DecimalField(_('remise'), max_digits=12, decimal_places=2, default=0)
    montant_ligne = models.DecimalField(_('montant ligne'), max_digits=15, decimal_places=2)

    class Meta:
        verbose_name = _('Ligne de Commande')
        verbose_name_plural = _('Lignes de Commande')

    def __str__(self):
        return f"{self.produit.nom} x{self.quantite}"

    def save(self, *args, **kwargs):
        self.montant_ligne = (self.prix_unitaire * self.quantite) - self.remise
        super().save(*args, **kwargs)
        # Recalculer le total de la commande
        self.commande.montant_total = sum(l.montant_ligne for l in self.commande.lignes.all())
        self.commande.save(update_fields=['montant_total'])


class Opportunite(models.Model):
    """Opportunité commerciale (pipeline de vente)"""

    class Etape(models.TextChoices):
        PROSPECT = 'PROSPECT', _('Prospect')
        QUALIFICATION = 'QUALIFICATION', _('Qualification')
        OFFRE = 'OFFRE', _('Offre envoyée')
        NEGOCIATION = 'NEGOCIATION', _('Négociation')
        GAGNE = 'GAGNE', _('Gagnée')
        PERDU = 'PERDU', _('Perdue')
        REPORTE = 'REPORTE', _('Reportée'),

    titre = models.CharField(_('titre'), max_length=200)
    description = models.TextField(_('description'), blank=True)

    commercial = models.ForeignKey(
        'commerciaux.Commercial',
        on_delete=models.CASCADE,
        related_name='opportunites',
        verbose_name=_('commercial'),
    )
    client = models.ForeignKey(
        'clients.Client',
        on_delete=models.CASCADE,
        related_name='opportunites',
        verbose_name=_('client prospect'),
    )

    # Pipeline
    etape = models.CharField(_('étape'), max_length=20, choices=Etape.choices, default=Etape.PROSPECT, db_index=True)
    probabilite = models.PositiveSmallIntegerField(
        _('probabilité (%)'),
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=20,
    )

    # Montants
    montant_estime = models.DecimalField(_('montant estimé'), max_digits=15, decimal_places=2, default=0)
    montant_final = models.DecimalField(_('montant final'), max_digits=15, decimal_places=2, null=True, blank=True)

    # Dates
    date_creation = models.DateTimeField(_('date création'), auto_now_add=True)
    date_cloture_prevue = models.DateField(_('date clôture prévue'), null=True, blank=True)
    date_cloture_effective = models.DateField(_('date clôture effective'), null=True, blank=True)

    # Source
    source = models.CharField(_('source'), max_length=100, blank=True)
    concurrence = models.CharField(_('concurrence'), max_length=200, blank=True)

    # Suivi
    notes = models.TextField(_('notes de suivi'), blank=True)
    prochaine_action = models.CharField(_('prochaine action'), max_length=200, blank=True)
    date_prochaine_action = models.DateTimeField(_('date prochaine action'), null=True, blank=True)

    # Commande liée (si gagnée)
    commande = models.OneToOneField(
        Commande,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='opportunite',
        verbose_name=_('commande associée'),
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Opportunité')
        verbose_name_plural = _('Opportunités')
        ordering = ['-date_creation']
        indexes = [
            models.Index(fields=['commercial', 'etape']),
            models.Index(fields=['client', 'etape']),
            models.Index(fields=['etape', 'date_cloture_prevue']),
        ]

    def __str__(self):
        return f"{self.titre} - {self.client.raison_sociale} ({self.get_etape_display()})"

    @property
    def is_gagnee(self):
        return self.etape == self.Etape.GAGNE

    @property
    def is_perdue(self):
        return self.etape == self.Etape.PERDU

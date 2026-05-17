"""
Modèles pour les KPIs et analytics (vues matérialisées / agrégations)
"""
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class KPIJournalier(models.Model):
    """KPIs agrégés par jour pour performance dashboard"""

    date = models.DateField(_('date'), db_index=True)
    commercial = models.ForeignKey(
        'commerciaux.Commercial',
        on_delete=models.CASCADE,
        related_name='kpis',
        null=True,
        blank=True,
        verbose_name=_('commercial'),
    )

    # Visites
    nombre_visites_planifiees = models.PositiveIntegerField(_('visites planifiées'), default=0)
    nombre_visites_effectuees = models.PositiveIntegerField(_('visites effectuées'), default=0)
    nombre_visites_annulees = models.PositiveIntegerField(_('visites annulées'), default=0)
    duree_moyenne_visite = models.PositiveIntegerField(_('durée moyenne visite (min)'), default=0)

    # Commandes
    nombre_commandes = models.PositiveIntegerField(_('commandes'), default=0)
    ca_total = models.DecimalField(_('CA total'), max_digits=15, decimal_places=2, default=0)
    ca_moyen_par_commande = models.DecimalField(_('CA moyen/commande'), max_digits=15, decimal_places=2, default=0)

    # Opportunités
    nombre_opportunites_crees = models.PositiveIntegerField(_('opportunités créées'), default=0)
    nombre_opportunites_gagnees = models.PositiveIntegerField(_('opportunités gagnées'), default=0)
    montant_opportunites_gagnees = models.DecimalField(_('montant opportunités gagnées'), max_digits=15, decimal_places=2, default=0)

    # GPS
    distance_parcourue_km = models.DecimalField(_('distance parcourue (km)'), max_digits=10, decimal_places=2, default=0)
    nombre_positions = models.PositiveIntegerField(_('positions GPS'), default=0)

    # Taux
    taux_conversion = models.DecimalField(_('taux conversion (%)'), max_digits=5, decimal_places=2, default=0)
    taux_objectif = models.DecimalField(_('taux objectif (%)'), max_digits=5, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('KPI Journalier')
        verbose_name_plural = _('KPIs Journaliers')
        ordering = ['-date']
        unique_together = [['date', 'commercial']]

    def __str__(self):
        return f"KPI {self.date} - {self.commercial.nom_complet if self.commercial else 'Global'}"

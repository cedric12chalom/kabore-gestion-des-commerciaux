"""
Modèles : Notification, Message (messagerie interne)
"""
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class Notification(models.Model):
    """Notification push temps réel"""

    class Type(models.TextChoices):
        NOUVELLE_VISITE = 'VISITE', _('Nouvelle visite assignée')
        COMMANDE_VALIDE = 'COMMANDE', _('Commande validée')
        OBJECTIF_ATTEINT = 'OBJECTIF', _('Objectif atteint')
        SORTIE_ZONE = 'ZONE', _('Sortie de zone')
        INACTIVITE = 'INACTIVITE', _('Alerte inactivité')
        MESSAGE = 'MESSAGE', _('Nouveau message')
        SYSTEME = 'SYSTEME', _('Notification système'),

    class Priorite(models.TextChoices):
        BASSE = 'BASSE', _('Basse')
        NORMALE = 'NORMALE', _('Normale')
        HAUTE = 'HAUTE', _('Haute')
        URGENTE = 'URGENTE', _('Urgente'),

    destinataire = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name=_('destinataire'),
    )

    type = models.CharField(_('type'), max_length=20, choices=Type.choices)
    priorite = models.CharField(_('priorité'), max_length=20, choices=Priorite.choices, default=Priorite.NORMALE)

    titre = models.CharField(_('titre'), max_length=200)
    message = models.TextField(_('message'))

    # Lien vers l'objet concerné
    objet_type = models.CharField(_("type d'objet"), max_length=50, blank=True)
    objet_id = models.PositiveIntegerField(_('ID objet'), null=True, blank=True)

    # Statut
    is_lue = models.BooleanField(_('lue'), default=False)
    is_envoyee = models.BooleanField(_('envoyée'), default=False)

    # Dates
    date_creation = models.DateTimeField(_('date création'), auto_now_add=True)
    date_lecture = models.DateTimeField(_('date lecture'), null=True, blank=True)

    class Meta:
        verbose_name = _('Notification')
        verbose_name_plural = _('Notifications')
        ordering = ['-date_creation']
        indexes = [
            models.Index(fields=['destinataire', 'is_lue']),
            models.Index(fields=['type', 'date_creation']),
        ]

    def __str__(self):
        return f"{self.titre} → {self.destinataire.email}"


class Message(models.Model):
    """Messagerie interne entre commercial et manager"""

    expediteur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='messages_envoyes',
        verbose_name=_('expéditeur'),
    )
    destinataire = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='messages_recus',
        verbose_name=_('destinataire'),
    )

    contenu = models.TextField(_('contenu'))

    # Liens métier (optionnel)
    client = models.ForeignKey(
        'clients.Client',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='messages',
        verbose_name=_('client lié'),
    )
    visite = models.ForeignKey(
        'visites.Visite',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='messages',
        verbose_name=_('visite liée'),
    )

    # Statut
    is_lu = models.BooleanField(_('lu'), default=False)
    date_lecture = models.DateTimeField(_('date lecture'), null=True, blank=True)

    # Dates
    date_envoi = models.DateTimeField(_('date envoi'), auto_now_add=True)

    class Meta:
        verbose_name = _('Message')
        verbose_name_plural = _('Messages')
        ordering = ['-date_envoi']

    def __str__(self):
        return f"{self.expediteur.get_full_name()} → {self.destinataire.get_full_name()}"

"""
GeoCommerce Pro - Modeles de base
Classe abstraite TimestampedModel pour tous les modeles du projet
"""
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class TimestampedModel(models.Model):
    """
    Modele abstrait de base pour tous les modeles GeoCommerce.
    Ajoute automatiquement created_at et updated_at a chaque enregistrement.

    Avantages :
    - Pas besoin de redefinir ces champs dans chaque modele
    - Traçabilite temporelle automatique
    - Soft delete possible via is_active
    """
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name="Cree le"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Modifie le"
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Actif",
        help_text="Soft delete : mettre a False pour archiver sans supprimer"
    )

    class Meta:
        abstract = True
        ordering = ['-created_at']


class AuditLog(models.Model):
    """
    Table d'audit : enregistre toutes les modifications importantes.
    Permet de savoir QUI a modifie QUOI et QUAND.
    """
    ACTION_CHOICES = [
        ('CREATE', 'Creation'),
        ('UPDATE', 'Modification'),
        ('DELETE', 'Suppression'),
        ('LOGIN', 'Connexion'),
        ('LOGOUT', 'Deconnexion'),
        ('GPS', 'Position GPS'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
        verbose_name="Utilisateur"
    )
    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        verbose_name="Action"
    )
    model_name = models.CharField(
        max_length=100,
        verbose_name="Modele concerne"
    )
    object_id = models.CharField(
        max_length=100,
        verbose_name="ID objet"
    )
    old_values = models.JSONField(
        null=True,
        blank=True,
        verbose_name="Anciennes valeurs"
    )
    new_values = models.JSONField(
        null=True,
        blank=True,
        verbose_name="Nouvelles valeurs"
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="Adresse IP"
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name="Date/Heure"
    )

    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Log d'audit"
        verbose_name_plural = "Logs d'audit"
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['model_name', 'timestamp']),
        ]

"""
Modèle Utilisateur personnalisé avec rôles (Admin, Manager, Commercial)
Basé sur AbstractUser pour garder toute la logique d'authentification Django
"""
import os
import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator


def user_photo_path(instance, filename):
    """Chemin de stockage des photos de profil"""
    ext = filename.split('.')[-1]
    return f'users/photos/{instance.id}_{uuid.uuid4().hex[:8]}.{ext}'


class User(AbstractUser):
    """
    Utilisateur GeoCommerce Pro avec authentification par email.
    3 rôles : ADMIN, MANAGER, COMMERCIAL
    """

    class Role(models.TextChoices):
        ADMIN = 'ADMIN', _('Administrateur')
        MANAGER = 'MANAGER', _('Manager')
        COMMERCIAL = 'COMMERCIAL', _('Commercial')

    # Email comme identifiant secondaire (unique et obligatoire)
    email = models.EmailField(
        _('adresse email'),
        unique=True,
        blank=False,
        error_messages={
            'unique': _('Un utilisateur avec cet email existe déjà.'),
        }
    )

    # Rôle utilisateur
    role = models.CharField(
        _('rôle'),
        max_length=20,
        choices=Role.choices,
        default=Role.COMMERCIAL,
        db_index=True,
    )

    # Profil
    first_name = models.CharField(_('prénom'), max_length=150, blank=False)
    last_name = models.CharField(_('nom'), max_length=150, blank=False)
    phone = models.CharField(
        _('téléphone'),
        max_length=20,
        blank=True,
        validators=[RegexValidator(
            regex=r'^\+?[0-9\s\-\(\)]+$',
            message=_('Format de téléphone invalide. Ex: +237 6XX XXX XXX')
        )]
    )
    photo = models.ImageField(
        _('photo de profil'),
        upload_to=user_photo_path,
        blank=True,
        null=True,
    )

    # Statut
    is_active = models.BooleanField(_('actif'), default=True, db_index=True)
    date_joined = models.DateTimeField(_("date d'inscription"), auto_now_add=True)
    last_modified = models.DateTimeField(_('dernière modification'), auto_now=True)

    # Manager associé (pour les commerciaux)
    manager = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='team_members',
        limit_choices_to={'role': Role.MANAGER},
        verbose_name=_('manager responsable'),
    )

    # Configuration auth
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    class Meta:
        verbose_name = _('Utilisateur')
        verbose_name_plural = _('Utilisateurs')
        ordering = ['-date_joined']
        indexes = [
            models.Index(fields=['email', 'role']),
            models.Index(fields=['role', 'is_active']),
            models.Index(fields=['manager', 'role']),
        ]

    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.email

    def get_short_name(self):
        return self.first_name or self.email.split('@')[0]

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN or self.is_superuser

    @property
    def is_manager(self):
        return self.role == self.Role.MANAGER

    @property
    def is_commercial(self):
        return self.role == self.Role.COMMERCIAL

    def get_team(self):
        """Retourne les membres de l'équipe (pour un manager)"""
        if self.is_manager:
            return User.objects.filter(manager=self, is_active=True)
        return User.objects.none()

    def save(self, *args, **kwargs):
        # Normaliser l'email en minuscules
        if self.email:
            self.email = self.email.lower().strip()
        super().save(*args, **kwargs)

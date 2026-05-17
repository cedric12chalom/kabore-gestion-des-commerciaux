"""
Signals GPS : alertes inactivité, nettoyage historique
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta

from .models import PositionGPS, AlerteZone
from apps.notifications.models import Notification


@receiver(post_save, sender=PositionGPS)
def check_inactivite(sender, instance, created, **kwargs):
    """Vérifier l'inactivité après chaque position"""
    if not created:
        return

    commercial = instance.commercial

    # Vérifier si le commercial est dans sa zone
    if commercial.zone and commercial.zone.polygone:
        if not commercial.zone.polygone.contains(instance.position):
            distance = instance.position.distance(commercial.zone.polygone.boundary)

            # Créer une alerte de sortie de zone
            alerte = AlerteZone.objects.create(
                commercial=commercial,
                zone=commercial.zone,
                type_alerte='SORTIE',
                position=instance.position,
                distance_zone_m=distance,
                message=f"{commercial.nom_complet} est sorti de la zone {commercial.zone.nom}",
            )

            # Notifier le manager
            if commercial.user.manager:
                Notification.objects.create(
                    destinataire=commercial.user.manager,
                    type='ZONE',
                    priorite='HAUTE',
                    titre=f"Alerte zone - {commercial.nom_complet}",
                    message=alerte.message,
                    objet_type='AlerteZone',
                    objet_id=alerte.id,
                )

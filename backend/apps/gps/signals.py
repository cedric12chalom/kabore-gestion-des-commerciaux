"""
Signaux GPS — alertes sortie de zone
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import HistoriqueParcours, AlerteZone


@receiver(post_save, sender=HistoriqueParcours)
def check_zone_on_position(sender, instance, created, **kwargs):
    if not created:
        return
    commercial = instance.commercial
    zone_assignee = commercial.zone_active
    if not zone_assignee or not zone_assignee.polygone:
        return
    try:
        if not zone_assignee.polygone.contains(instance.position):
            AlerteZone.objects.create(
                commercial=commercial,
                zone_assignee=zone_assignee,
                type_alerte='SORTIE',
                position=instance.position,
                message=f"{commercial.nom_complet} est sorti de la zone {zone_assignee.nom}",
            )
    except Exception:
        pass

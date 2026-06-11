"""
Tâches GPS : détection hors-ligne + purge historique.
Utilisable via Celery ou management command.
"""
from django.utils import timezone
from .models import PositionTempsReel, HistoriqueParcours


def marquer_commerciaux_offline():
    """Marque offline les commerciaux sans update depuis 2 min."""
    seuil = timezone.now() - timezone.timedelta(seconds=PositionTempsReel.seuil_hors_ligne_secondes())
    return PositionTempsReel.objects.filter(online=True, dernier_update__lt=seuil).update(online=False)


def purger_historique_parcours(jours: int = 30):
    return HistoriqueParcours.purger_ancien(jours)

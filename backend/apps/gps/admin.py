from django.contrib import admin
from django.conf import settings
from .models import PositionTempsReel, HistoriqueParcours, AlerteZone

if settings.USE_GIS:
    from django.contrib.gis.admin import GISModelAdmin as BaseAdmin
else:
    BaseAdmin = admin.ModelAdmin


@admin.register(PositionTempsReel)
class PositionTempsReelAdmin(BaseAdmin):
    list_display = ['commercial', 'online', 'dernier_update', 'precision']


@admin.register(HistoriqueParcours)
class HistoriqueParcoursAdmin(BaseAdmin):
    list_display = ['commercial', 'timestamp', 'precision']


@admin.register(AlerteZone)
class AlerteZoneAdmin(BaseAdmin):
    list_display = ['commercial', 'type_alerte', 'statut', 'timestamp']

"""
Admin Django pour GPS
"""
from django.contrib import admin
from django.conf import settings
from .models import PositionGPS, HistoriqueParcours, AlerteZone

if settings.USE_GIS:
    from django.contrib.gis.admin import GISModelAdmin
else:
    GISModelAdmin = admin.ModelAdmin


@admin.register(PositionGPS)
class PositionGPSAdmin(GISModelAdmin):
    list_display = ['commercial', 'latitude', 'longitude', 'vitesse', 'timestamp', 'source']
    list_filter = ['source', 'timestamp']
    search_fields = ['commercial__user__first_name', 'commercial__user__last_name']
    date_hierarchy = 'timestamp'


@admin.register(AlerteZone)
class AlerteZoneAdmin(GISModelAdmin):
    list_display = ['commercial', 'zone', 'type_alerte', 'statut', 'timestamp']
    list_filter = ['type_alerte', 'statut']

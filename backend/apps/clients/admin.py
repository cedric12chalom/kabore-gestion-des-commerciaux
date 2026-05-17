"""
Admin Django pour Clients
"""
from django.contrib import admin
from django.conf import settings
from .models import Client

if settings.USE_GIS:
    from django.contrib.gis.admin import GISModelAdmin
else:
    GISModelAdmin = admin.ModelAdmin


@admin.register(Client)
class ClientAdmin(GISModelAdmin):
    list_display = [
        'raison_sociale', 'ville', 'secteur', 'potentiel',
        'commercial_referent', 'is_actif', 'date_creation',
    ]
    list_filter = ['ville', 'secteur', 'potentiel', 'is_actif']
    search_fields = ['raison_sociale', 'nom_contact', 'email', 'telephone']
    gis_widget_kwargs = {
        'attrs': {
            'default_zoom': 12,
            'default_lon': 9.7680,
            'default_lat': 4.0511,
        }
    }

"""
App config GPS
"""
from django.apps import AppConfig


class GpsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.gps'
    verbose_name = 'Géolocalisation GPS'

    def ready(self):
        import apps.gps.signals

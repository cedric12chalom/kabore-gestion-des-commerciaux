"""
Admin Django pour Dashboard
"""
from django.contrib import admin
from .models import KPIJournalier


@admin.register(KPIJournalier)
class KPIAdmin(admin.ModelAdmin):
    list_display = ['date', 'commercial', 'ca_total', 'nombre_visites_effectuees', 'distance_parcourue_km']
    list_filter = ['date']

"""
Admin Django pour Visites
"""
from django.contrib import admin
from .models import Visite, RapportVisite


class RapportInline(admin.StackedInline):
    model = RapportVisite
    extra = 0


@admin.register(Visite)
class VisiteAdmin(admin.ModelAdmin):
    list_display = [
        'client', 'commercial', 'date_prevue', 'statut',
        'duree_reelle', 'is_validee', 'satisfaction_client',
    ]
    list_filter = ['statut', 'type_visite', 'date_prevue']
    search_fields = ['client__raison_sociale', 'compte_rendu']
    inlines = [RapportInline]
    date_hierarchy = 'date_prevue'

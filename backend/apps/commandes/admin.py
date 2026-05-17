"""
Admin Django pour Commandes
"""
from django.contrib import admin
from .models import Commande, LigneCommande, Opportunite


class LigneInline(admin.TabularInline):
    model = LigneCommande
    extra = 1
    readonly_fields = ['montant_ligne']


@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    list_display = [
        'reference', 'client', 'commercial', 'montant_total',
        'statut', 'date', 'date_livraison_prevue',
    ]
    list_filter = ['statut', 'date']
    search_fields = ['reference', 'client__raison_sociale']
    inlines = [LigneInline]
    date_hierarchy = 'date'


@admin.register(Opportunite)
class OpportuniteAdmin(admin.ModelAdmin):
    list_display = ['titre', 'client', 'commercial', 'etape', 'probabilite', 'montant_estime']
    list_filter = ['etape', 'date_creation']
    search_fields = ['titre', 'client__raison_sociale']

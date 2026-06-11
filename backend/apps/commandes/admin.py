from django.contrib import admin
from .models import Commande, LigneCommande, Opportunite


class LigneInline(admin.TabularInline):
    model = LigneCommande
    extra = 1
    readonly_fields = ['montant_ligne']


@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    list_display = ['reference', 'contact_nom', 'commercial', 'montant_total', 'statut', 'date']
    list_filter = ['statut', 'date']
    search_fields = ['reference', 'contact_nom', 'quartier']
    inlines = [LigneInline]


@admin.register(Opportunite)
class OpportuniteAdmin(admin.ModelAdmin):
    list_display = ['titre', 'contact_nom', 'commercial', 'etape', 'montant_estime']
    list_filter = ['etape']
    search_fields = ['titre', 'contact_nom']

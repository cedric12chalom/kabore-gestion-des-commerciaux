"""
Admin Django pour Commerciaux
"""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Commercial, Telephone, Zone, ObjectifCommercial, Produit


class TelephoneInline(admin.TabularInline):
    model = Telephone
    extra = 1
    fields = ['numero', 'type', 'is_principal', 'is_whatsapp']


@admin.register(Commercial)
class CommercialAdmin(admin.ModelAdmin):
    list_display = [
        'matricule', 'nom_complet', 'statut', 'zone',
        'objectif_mensuel', 'date_embauche', 'total_ventes',
    ]
    list_filter = ['statut', 'zone', 'date_embauche']
    search_fields = ['matricule', 'user__first_name', 'user__last_name', 'user__email']
    inlines = [TelephoneInline]
    readonly_fields = ['created_at', 'updated_at']

    def nom_complet(self, obj):
        return obj.nom_complet
    nom_complet.short_description = 'Nom'


@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = ['nom', 'ville', 'pays', 'manager', 'is_active', 'surface_km2']
    list_filter = ['ville', 'pays', 'is_active']
    search_fields = ['nom', 'ville']


@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display = ['reference', 'nom', 'categorie', 'prix_unitaire', 'stock', 'is_active']
    list_filter = ['categorie', 'is_active']
    search_fields = ['reference', 'nom']


@admin.register(ObjectifCommercial)
class ObjectifAdmin(admin.ModelAdmin):
    list_display = ['commercial', 'periode', 'montant_cible', 'montant_atteint', 'taux_realisation', 'is_atteint']
    list_filter = ['periode', 'is_atteint']

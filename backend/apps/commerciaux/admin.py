from django.contrib import admin
from .models import Commercial, Telephone, Zone, ZoneAssignee, ObjectifCommercial, Produit


class TelephoneInline(admin.TabularInline):
    model = Telephone
    extra = 1


@admin.register(Commercial)
class CommercialAdmin(admin.ModelAdmin):
    list_display = ['matricule', 'nom_complet', 'statut', 'manager', 'date_embauche']
    list_filter = ['statut', 'date_embauche']
    search_fields = ['matricule', 'user__email']
    inlines = [TelephoneInline]

    def nom_complet(self, obj):
        return obj.nom_complet


@admin.register(ZoneAssignee)
class ZoneAssigneeAdmin(admin.ModelAdmin):
    list_display = ['nom', 'commercial', 'manager', 'active', 'date_debut', 'date_fin']


@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = ['nom', 'ville', 'manager', 'is_active']


@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display = ['reference', 'nom', 'prix_unitaire', 'stock', 'is_active']


@admin.register(ObjectifCommercial)
class ObjectifAdmin(admin.ModelAdmin):
    list_display = ['commercial', 'periode', 'annee', 'mois', 'cible', 'realise', 'is_atteint']

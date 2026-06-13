from django.contrib import admin
from .models import Visite, RapportVisite


class RapportInline(admin.StackedInline):
    model = RapportVisite
    extra = 0


@admin.register(Visite)
class VisiteAdmin(admin.ModelAdmin):
    list_display = ['point_vente_nom', 'manager', 'date_prevue', 'statut', 'is_validee']
    list_filter = ['statut', 'type_visite']
    search_fields = ['point_vente_nom', 'compte_rendu']
    inlines = [RapportInline]

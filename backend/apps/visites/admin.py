from django.contrib import admin
from .models import Visite, RapportVisite


class RapportInline(admin.StackedInline):
    model = RapportVisite
    extra = 0


@admin.register(Visite)
class VisiteAdmin(admin.ModelAdmin):
    list_display = ['contact_nom', 'commercial', 'date_prevue', 'statut', 'is_validee']
    list_filter = ['statut', 'type_visite']
    search_fields = ['contact_nom', 'compte_rendu']
    inlines = [RapportInline]

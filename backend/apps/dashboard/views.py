"""
Views pour Dashboards et Analytics
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
import csv

from .analytics import AnalyticsManager
from apps.users.permissions import IsAdminOrManager, IsCommercial


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminOrManager])
def dashboard_manager_view(request):
    """
    GET /api/v1/dashboard/manager/
    KPIs complets pour manager/admin
    """
    date_debut = request.query_params.get('date_debut')
    date_fin = request.query_params.get('date_fin')
    
    try:
        data = AnalyticsManager.get_kpis_manager(date_debut, date_fin)
        return Response({
            'success': True,
            'data': data
        })
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_commercial_view(request):
    """
    GET /api/v1/dashboard/commercial/
    KPIs pour le commercial connecté
    """
    user = request.user
    
    if not hasattr(user, 'commercial_profile'):
        return Response({
            'success': False,
            'error': 'Vous n\'êtes pas un commercial.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    date_debut = request.query_params.get('date_debut')
    date_fin = request.query_params.get('date_fin')
    
    try:
        data = AnalyticsManager.get_kpis_commercial(
            user.commercial_profile.id,
            date_debut,
            date_fin
        )
        return Response({
            'success': True,
            'data': data
        })
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_rapport_view(request):
    """
    GET /api/v1/dashboard/export/
    Export CSV des données
    """
    format_export = request.query_params.get('format', 'csv')
    date_debut = request.query_params.get('date_debut')
    date_fin = request.query_params.get('date_fin')
    
    if format_export != 'csv':
        return Response({
            'success': False,
            'error': 'Format non supporté. Utilisez format=csv'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    user = request.user
    
    try:
        # Récupérer les données appropriées
        if user.is_admin or user.is_manager:
            kpis = AnalyticsManager.get_kpis_manager(date_debut, date_fin)
        else:
            if not hasattr(user, 'commercial_profile'):
                return Response({
                    'success': False,
                    'error': 'Pas de profil commercial.'
                }, status=status.HTTP_403_FORBIDDEN)
            kpis = AnalyticsManager.get_kpis_commercial(
                user.commercial_profile.id,
                date_debut,
                date_fin
            )
        
        # Créer le CSV
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="rapport_{}.csv"'.format(
            kpis.get('periode', {}).get('fin', 'export').split('T')[0]
        )
        
        writer = csv.writer(response)
        
        # En-têtes
        writer.writerow(['GeoCommerce Pro - Rapport d\'Analytics'])
        writer.writerow(['Période', kpis.get('periode', {}).get('debut'), 'à', kpis.get('periode', {}).get('fin')])
        writer.writerow([])
        
        # Ventes
        writer.writerow(['VENTES'])
        ventes = kpis.get('ventes', {})
        writer.writerow(['Nombre de commandes', ventes.get('total', 0)])
        writer.writerow(['Montant total (XAF)', ventes.get('montant_total', 0)])
        writer.writerow(['Montant moyen (XAF)', ventes.get('montant_moyen', 0)])
        writer.writerow([])
        
        # Visites
        writer.writerow(['VISITES'])
        visites = kpis.get('visites', {})
        writer.writerow(['Total', visites.get('total', 0)])
        writer.writerow(['Effectuées', visites.get('effectuees', 0)])
        writer.writerow(['Planifiées', visites.get('planifiees', 0)])
        writer.writerow(['Annulées', visites.get('annulees', 0)])
        writer.writerow(['Taux conversion (%)', visites.get('taux_conversion', 0)])
        writer.writerow([])
        
        # Commerciaux
        writer.writerow(['COMMERCIAUX'])
        commerciaux = kpis.get('commerciaux', {})
        writer.writerow(['Total actifs', commerciaux.get('total', 0)])
        obj_atteints = commerciaux.get('objectifs_atteints', {})
        writer.writerow(['Objectifs atteints', obj_atteints.get('atteints', 0)])
        writer.writerow(['Taux objectif (%)', obj_atteints.get('taux', 0)])
        writer.writerow([])
        
        # Top performers
        writer.writerow(['Top Performers'])
        writer.writerow(['Rang', 'Nom', 'Matricule', 'Total Ventes (XAF)', 'Nombre Ventes'])
        for i, performer in enumerate(commerciaux.get('top_performers', []), 1):
            writer.writerow([
                i,
                performer.get('nom'),
                performer.get('matricule'),
                performer.get('total_ventes', 0),
                performer.get('nombre_ventes', 0),
            ])
        writer.writerow([])
        
        # Clients
        writer.writerow(['CLIENTS'])
        clients = kpis.get('clients', {})
        contacts = kpis.get('contacts', clients)
        writer.writerow(['Total', contacts.get('total', 0)])
        writer.writerow(['Nouveaux', contacts.get('nouveaux', 0)])
        
        return response
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def rapports_view(request):
    """
    GET /api/v1/dashboard/rapports/
    Données pour les rapports et graphiques
    Optionnel pour maintenant - endpoint hérité
    """
    user = request.user
    
    try:
        if user.is_admin or user.is_manager:
            data = AnalyticsManager.get_kpis_manager()
        else:
            if not hasattr(user, 'commercial_profile'):
                return Response({
                    'success': False,
                    'error': 'Pas de profil commercial.'
                }, status=status.HTTP_403_FORBIDDEN)
            data = AnalyticsManager.get_kpis_commercial(user.commercial_profile.id)
        
        return Response({
            'success': True,
            'data': data
        })
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
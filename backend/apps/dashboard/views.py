"""
Views pour Dashboards et Analytics
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q, Count, Sum, Avg, F
from django.utils import timezone
from datetime import timedelta, date
import calendar

from apps.commerciaux.models import Commercial
from apps.clients.models import Client
from apps.visites.models import Visite
from apps.commandes.models import Commande, Opportunite
from apps.gps.models import PositionGPS, HistoriqueParcours


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_manager_view(request):
    """GET /api/v1/dashboard/manager/ - Vue globale pour le manager/admin"""
    user = request.user

    # Déterminer le scope des données
    if user.is_admin:
        commerciaux_qs = Commercial.objects.filter(statut='ACTIF')
        clients_qs = Client.objects.filter(is_actif=True)
        visites_qs = Visite.objects.all()
        commandes_qs = Commande.objects.all()
    elif user.is_manager:
        team = user.get_team()
        commerciaux_ids = [u.commercial_profile.id for u in team if hasattr(u, 'commercial_profile')]
        commerciaux_qs = Commercial.objects.filter(id__in=commerciaux_ids, statut='ACTIF')
        clients_qs = Client.objects.filter(commercial_referent__user__in=team, is_actif=True)
        visites_qs = Visite.objects.filter(commercial__user__in=team)
        commandes_qs = Commande.objects.filter(commercial__user__in=team)
    else:
        return Response({'success': False, 'error': 'Accès réservé aux managers et admins'}, status=403)

    # Période : aujourd'hui
    today = timezone.now().date()
    debut_mois = today.replace(day=1)

    # KPIs
    kpis = {
        'commerciaux_actifs': commerciaux_qs.count(),
        'clients_total': clients_qs.count(),
        'visites_jour': visites_qs.filter(date_prevue__date=today).count(),
        'visites_mois': visites_qs.filter(date_prevue__date__gte=debut_mois).count(),
        'commandes_jour': commandes_qs.filter(date__date=today).count(),
        'ca_mois': commandes_qs.filter(
            date__date__gte=debut_mois,
            statut__in=['VALIDEE', 'LIVREE']
        ).aggregate(total=Sum('montant_total'))['total'] or 0,
        'taux_conversion': calculate_taux_conversion(visites_qs, commandes_qs),
    }

    # Commerciaux en ligne (position récente)
    limite = timezone.now() - timedelta(minutes=5)
    en_ligne = PositionGPS.objects.filter(
        timestamp__gte=limite,
        commercial__in=commerciaux_qs,
    ).values('commercial').distinct().count()

    kpis['commerciaux_en_ligne'] = en_ligne

    # Top commerciaux du mois
    top_commerciaux = []
    for com in commerciaux_qs[:5]:
        ca = Commande.objects.filter(
            commercial=com,
            date__date__gte=debut_mois,
            statut__in=['VALIDEE', 'LIVREE']
        ).aggregate(total=Sum('montant_total'))['total'] or 0

        visites = Visite.objects.filter(
            commercial=com,
            date_prevue__date__gte=debut_mois,
            statut='EFFECTUEE'
        ).count()

        top_commerciaux.append({
            'id': com.id,
            'nom': com.nom_complet,
            'matricule': com.matricule,
            'ca_mois': ca,
            'visites_mois': visites,
            'taux_objectif': com.taux_objectif_mensuel,
        })

    top_commerciaux.sort(key=lambda x: x['ca_mois'], reverse=True)

    # Alertes récentes
    from apps.gps.models import AlerteZone
    alertes = AlerteZone.objects.filter(
        commercial__in=commerciaux_qs,
        statut='NOUVELLE',
    ).order_by('-timestamp')[:5]

    alertes_data = []
    for alerte in alertes:
        alertes_data.append({
            'id': alerte.id,
            'type': alerte.get_type_alerte_display(),
            'commercial': alerte.commercial.nom_complet,
            'message': alerte.message,
            'timestamp': alerte.timestamp.isoformat(),
        })

    return Response({
        'success': True,
        'kpis': kpis,
        'top_commerciaux': top_commerciaux,
        'alertes': alertes_data,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_commercial_view(request):
    """GET /api/v1/dashboard/commercial/ - Vue personnelle du commercial"""
    user = request.user

    if not user.is_commercial:
        return Response({'success': False, 'error': 'Accès réservé aux commerciaux'}, status=403)

    try:
        commercial = user.commercial_profile
    except:
        return Response({'success': False, 'error': 'Profil commercial non trouvé'}, status=404)

    today = timezone.now().date()
    debut_mois = today.replace(day=1)

    # Agenda du jour
    visites_jour = Visite.objects.filter(
        commercial=commercial,
        date_prevue__date=today,
    ).order_by('date_prevue')

    agenda = []
    for v in visites_jour:
        agenda.append({
            'id': v.id,
            'client': v.client.raison_sociale,
            'heure': v.date_prevue.strftime('%H:%M'),
            'statut': v.statut,
            'type': v.get_type_visite_display(),
            'adresse': v.client.adresse,
            'position': {'lat': v.client.latitude, 'lng': v.client.longitude} if v.client.position else None,
        })

    # Objectifs
    objectifs = []
    for obj in commercial.objectifs.filter(date_debut__lte=today, date_fin__gte=today):
        objectifs.append({
            'periode': obj.get_periode_display(),
            'montant_cible': obj.montant_cible,
            'montant_atteint': obj.montant_atteint,
            'taux_realisation': obj.taux_realisation,
            'is_atteint': obj.is_atteint,
        })

    # Stats mois
    ca_mois = Commande.objects.filter(
        commercial=commercial,
        date__date__gte=debut_mois,
        statut__in=['VALIDEE', 'LIVREE']
    ).aggregate(total=Sum('montant_total'))['total'] or 0

    visites_mois = Visite.objects.filter(
        commercial=commercial,
        date_prevue__date__gte=debut_mois,
        statut='EFFECTUEE'
    ).count()

    # Distance parcourue aujourd'hui
    distance_jour = commercial.distance_totale_jour

    return Response({
        'success': True,
        'commercial': {
            'nom': commercial.nom_complet,
            'matricule': commercial.matricule,
            'statut': commercial.get_statut_display(),
            'zone': commercial.zone.nom if commercial.zone else None,
        },
        'agenda_jour': agenda,
        'objectifs': objectifs,
        'stats_mois': {
            'ca': ca_mois,
            'visites': visites_mois,
            'distance_jour_km': distance_jour,
            'taux_objectif': commercial.taux_objectif_mensuel,
        },
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def rapports_view(request):
    """GET /api/v1/dashboard/rapports/ - Données pour rapports et graphiques"""
    user = request.user
    periode = request.query_params.get('periode', 'mois')  # jour, semaine, mois, trimestre, annee

    # Déterminer les dates
    today = timezone.now().date()
    if periode == 'jour':
        date_debut = today
    elif periode == 'semaine':
        date_debut = today - timedelta(days=today.weekday())
    elif periode == 'mois':
        date_debut = today.replace(day=1)
    elif periode == 'trimestre':
        trimestre = (today.month - 1) // 3 + 1
        date_debut = today.replace(month=(trimestre - 1) * 3 + 1, day=1)
    else:  # annee
        date_debut = today.replace(month=1, day=1)

    # Scope
    if user.is_admin:
        visites_qs = Visite.objects.filter(date_prevue__date__gte=date_debut)
        commandes_qs = Commande.objects.filter(date__date__gte=date_debut)
    elif user.is_manager:
        team = user.get_team()
        visites_qs = Visite.objects.filter(commercial__user__in=team, date_prevue__date__gte=date_debut)
        commandes_qs = Commande.objects.filter(commercial__user__in=team, date__date__gte=date_debut)
    else:
        visites_qs = Visite.objects.filter(commercial__user=user, date_prevue__date__gte=date_debut)
        commandes_qs = Commande.objects.filter(commercial__user=user, date__date__gte=date_debut)

    # Visites par statut
    visites_par_statut = visites_qs.values('statut').annotate(
        count=Count('id')
    ).order_by('statut')

    # CA par jour (pour courbe)
    ca_par_jour = commandes_qs.filter(
        statut__in=['VALIDEE', 'LIVREE']
    ).values('date__date').annotate(
        ca=Sum('montant_total'),
        count=Count('id')
    ).order_by('date__date')

    # Visites par commercial (top 10)
    visites_par_commercial = visites_qs.filter(
        statut='EFFECTUEE'
    ).values('commercial__user__first_name', 'commercial__user__last_name').annotate(
        count=Count('id'),
        duree_moyenne=Avg('duree_reelle'),
    ).order_by('-count')[:10]

    # Opportunités par étape
    opportunites_par_etape = Opportunite.objects.filter(
        date_creation__date__gte=date_debut
    ).values('etape').annotate(
        count=Count('id'),
        montant=Sum('montant_estime'),
    ).order_by('etape')

    return Response({
        'success': True,
        'periode': periode,
        'date_debut': date_debut.isoformat(),
        'date_fin': today.isoformat(),
        'visites_par_statut': list(visites_par_statut),
        'ca_par_jour': list(ca_par_jour),
        'visites_par_commercial': list(visites_par_commercial),
        'opportunites_par_etape': list(opportunites_par_etape),
    })


def calculate_taux_conversion(visites_qs, commandes_qs):
    """Calcule le taux de conversion visites → commandes"""
    visites_effectuees = visites_qs.filter(statut='EFFECTUEE').count()
    commandes_validees = commandes_qs.filter(statut__in=['VALIDEE', 'LIVREE']).count()

    if visites_effectuees > 0:
        return round((commandes_validees / visites_effectuees) * 100, 2)
    return 0


# Import serializers
from rest_framework import serializers

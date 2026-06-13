"""
Analytics et KPIs pour le dashboard
"""
from django.db.models import Count, Sum, Avg, F
from django.utils import timezone
from datetime import timedelta, datetime
from apps.commandes.models import Commande, LigneCommande
from apps.visites.models import Visite
from apps.commerciaux.models import Commercial


class AnalyticsManager:
    """Calcul des KPIs pour le dashboard"""
    
    @staticmethod
    def parse_date(date_str):
        """Parse une date ISO string ou retourne None"""
        if not date_str:
            return None
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            return None
    
    @staticmethod
    def get_kpis_manager(date_debut=None, date_fin=None):
        """KPIs pour le dashboard manager/admin"""
        if not date_debut:
            date_debut = timezone.now() - timedelta(days=30)
        elif isinstance(date_debut, str):
            dt = AnalyticsManager.parse_date(date_debut)
            date_debut = dt if dt else timezone.now() - timedelta(days=30)
        
        if not date_fin:
            date_fin = timezone.now()
        elif isinstance(date_fin, str):
            dt = AnalyticsManager.parse_date(date_fin)
            date_fin = dt if dt else timezone.now()
        
        # Ventes
        ventes = Commande.objects.filter(
            date__gte=date_debut,
            date__lte=date_fin,
            statut__in=['EN_COURS', 'LIVREE']
        )
        
        # Visites
        visites = Visite.objects.filter(
            date_effective__gte=date_debut,
            date_effective__lte=date_fin
        )
        
        montant_total = ventes.aggregate(Sum('montant_total'))['montant_total__sum'] or 0
        montant_moyen = ventes.aggregate(Avg('montant_total'))['montant_total__avg'] or 0
        
        return {
            'periode': {
                'debut': date_debut.isoformat(),
                'fin': date_fin.isoformat()
            },
            'ventes': {
                'total': ventes.count(),
                'montant_total': float(montant_total),
                'montant_moyen': float(montant_moyen),
                'evolution': AnalyticsManager.get_evolution_ventes(date_debut, date_fin)
            },
            'visites': {
                'total': visites.count(),
                'effectuees': visites.filter(statut='EFFECTUEE').count(),
                'planifiees': visites.filter(statut='PLANIFIEE').count(),
                'annulees': visites.filter(statut='ANNULEE').count(),
                'taux_conversion': AnalyticsManager.get_taux_conversion(date_debut, date_fin)
            },
            'commerciaux': {
                'total': Commercial.objects.filter(statut='ACTIF').count(),
                'top_performers': AnalyticsManager.get_top_performers(date_debut, date_fin, 5),
                'objectifs_atteints': AnalyticsManager.get_objectifs_atteints(date_debut, date_fin)
            },
            'contacts': {
                'total': Commande.objects.values('contact_telephone').distinct().count(),
                'nouveaux': Commande.objects.filter(
                    date__gte=date_debut,
                    date__lte=date_fin,
                ).values('contact_telephone').distinct().count(),
            }
        }
    
    @staticmethod
    def get_kpis_commercial(commercial_id, date_debut=None, date_fin=None):
        """KPIs pour un commercial spécifique"""
        if not date_debut:
            date_debut = timezone.now() - timedelta(days=30)
        elif isinstance(date_debut, str):
            dt = AnalyticsManager.parse_date(date_debut)
            date_debut = dt if dt else timezone.now() - timedelta(days=30)
        
        if not date_fin:
            date_fin = timezone.now()
        elif isinstance(date_fin, str):
            dt = AnalyticsManager.parse_date(date_fin)
            date_fin = dt if dt else timezone.now()
        
        commercial = Commercial.objects.get(id=commercial_id)
        
        ventes = Commande.objects.filter(
            commercial=commercial,
            date__gte=date_debut,
            date__lte=date_fin,
            statut__in=['EN_COURS', 'LIVREE']
        )
        
        visites = Visite.objects.none()
        
        montant_total = ventes.aggregate(Sum('montant_total'))['montant_total__sum'] or 0
        duree_moyenne = visites.filter(statut='EFFECTUEE').aggregate(Avg('duree_reelle'))['duree_reelle__avg']
        
        from apps.commerciaux.models import ObjectifCommercial
        now = timezone.now()
        objectif = ObjectifCommercial.objects.filter(
            commercial=commercial,
            periode=ObjectifCommercial.Periode.MENSUEL,
            annee=now.year,
            mois=now.month,
        ).first()
        objectif_cible = float(objectif.cible) if objectif else 0

        return {
            'commercial': {
                'id': commercial.id,
                'nom': commercial.user.get_full_name(),
                'matricule': commercial.matricule,
                'objectif_mensuel': objectif_cible,
            },
            'ventes': {
                'total': ventes.count(),
                'montant_total': float(montant_total),
                'progression_objectif': AnalyticsManager.get_progression_objectif(commercial, montant_total)
            },
            'visites': {
                'total': visites.count(),
                'effectuees': visites.filter(statut='EFFECTUEE').count(),
                'duree_moyenne': float(duree_moyenne) if duree_moyenne else 0
            },
            'contacts': {
                'total': Commande.objects.filter(commercial=commercial).values('contact_telephone').distinct().count(),
            },
            'evolution': AnalyticsManager.get_evolution_ventes(date_debut, date_fin, commercial)
        }
    
    @staticmethod
    def get_evolution_ventes(date_debut, date_fin, commercial=None):
        """Évolution des ventes par jour"""
        from django.db.models.functions import TruncDate
        
        qs = Commande.objects.filter(
            date__gte=date_debut,
            date__lte=date_fin,
            statut__in=['EN_COURS', 'LIVREE']
        )
        
        if commercial:
            qs = qs.filter(commercial=commercial)
        
        ventes_par_jour = qs.annotate(
            jour=TruncDate('date')
        ).values('jour').annotate(
            total=Sum('montant_total'),
            nombre=Count('id')
        ).order_by('jour')
        
        return [
            {
                'date': v['jour'].isoformat() if v['jour'] else None,
                'montant': float(v['total'] or 0),
                'nombre_commandes': v['nombre']
            }
            for v in ventes_par_jour
        ]
    
    @staticmethod
    def get_top_performers(date_debut, date_fin, limit=5):
        """Top commerciaux par ventes"""
        result = []
        for commercial in Commercial.objects.filter(statut='ACTIF'):
            ventes = Commande.objects.filter(
                commercial=commercial,
                date__gte=date_debut,
                date__lte=date_fin,
                statut__in=['EN_COURS', 'LIVREE']
            )
            total_ventes = ventes.aggregate(Sum('montant_total'))['montant_total__sum'] or 0
            nombre_ventes = ventes.count()
            
            if total_ventes > 0 or nombre_ventes > 0:
                result.append({
                    'id': commercial.id,
                    'nom': commercial.user.get_full_name(),
                    'matricule': commercial.matricule,
                    'total_ventes': float(total_ventes),
                    'nombre_ventes': nombre_ventes
                })
        
        return sorted(result, key=lambda x: x['total_ventes'], reverse=True)[:limit]
    
    @staticmethod
    def get_taux_conversion(date_debut, date_fin):
        """Taux de conversion visites → commandes"""
        visites = Visite.objects.filter(
            date_effective__gte=date_debut,
            date_effective__lte=date_fin,
            statut='EFFECTUEE'
        ).count()
        
        commandes = Commande.objects.filter(
            date__gte=date_debut,
            date__lte=date_fin,
            statut__in=['EN_COURS', 'LIVREE']
        ).count()
        
        if visites == 0:
            return 0
        return round((commandes / visites) * 100, 2)
    
    @staticmethod
    def get_progression_objectif(commercial, montant_total):
        from apps.commerciaux.models import ObjectifCommercial
        now = timezone.now()
        obj = ObjectifCommercial.objects.filter(
            commercial=commercial,
            periode=ObjectifCommercial.Periode.MENSUEL,
            annee=now.year,
            mois=now.month,
        ).first()
        objectif = float(obj.cible) if obj else 0
        if objectif == 0:
            return 100
        progression = (float(montant_total) / objectif) * 100
        return min(round(progression, 2), 100)
    
    @staticmethod
    def get_objectifs_atteints(date_debut, date_fin):
        """Nombre de commerciaux ayant atteint leur objectif"""
        commerciaux = Commercial.objects.filter(statut='ACTIF')
        atteints = 0
        
        for commercial in commerciaux:
            ventes = Commande.objects.filter(
                commercial=commercial,
                date__gte=date_debut,
                date__lte=date_fin,
                statut__in=['EN_COURS', 'LIVREE']
            )
            montant_total = ventes.aggregate(Sum('montant_total'))['montant_total__sum'] or 0
            progression = AnalyticsManager.get_progression_objectif(commercial, montant_total)
            if progression >= 100:
                atteints += 1
        
        return {
            'atteints': atteints,
            'total': commerciaux.count(),
            'taux': round((atteints / commerciaux.count()) * 100, 2) if commerciaux.count() > 0 else 0
        }

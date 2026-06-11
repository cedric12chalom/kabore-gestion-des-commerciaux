import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { environment } from '../../environments/environment';
import { DashboardCommercial, DashboardManager } from '../models/dashboard.model';

@Injectable({
  providedIn: 'root'
})
export class DashboardService {
  private http = inject(HttpClient);
  private baseUrl = `${environment.apiUrl}/dashboard`;

  /**
   * Récupère les KPIs pour le manager/admin
   * @param dateDebut Format ISO string (ex: 2024-01-01)
   * @param dateFin Format ISO string (ex: 2024-01-31)
   */
  getKPIsManager(dateDebut?: string, dateFin?: string): Observable<any> {
    let params = new HttpParams();
    
    if (dateDebut) params = params.set('date_debut', dateDebut);
    if (dateFin) params = params.set('date_fin', dateFin);

    return this.http.get<any>(`${this.baseUrl}/manager/`, { params });
  }

  /**
   * Récupère les KPIs pour le commercial connecté
   * @param dateDebut Format ISO string
   * @param dateFin Format ISO string
   */
  getKPIsCommercial(dateDebut?: string, dateFin?: string): Observable<any> {
    let params = new HttpParams();
    
    if (dateDebut) params = params.set('date_debut', dateDebut);
    if (dateFin) params = params.set('date_fin', dateFin);

    return this.http.get<any>(`${this.baseUrl}/commercial/`, { params });
  }

  /**
   * Exporte les rapports en CSV
   * @param dateDebut Format ISO string
   * @param dateFin Format ISO string
   * @returns Observable<Blob> contenant le fichier CSV
   */
  exporterRapport(dateDebut?: string, dateFin?: string): Observable<Blob> {
    let params = new HttpParams();
    params = params.set('format', 'csv');
    
    if (dateDebut) params = params.set('date_debut', dateDebut);
    if (dateFin) params = params.set('date_fin', dateFin);

    return this.http.get<Blob>(`${this.baseUrl}/export/`, {
      params,
      responseType: 'blob' as 'json'
    });
  }

  // Méthodes héritées pour compatibilité
  getDashboardManager(): Observable<DashboardManager | null> {
    return this.getKPIsManager().pipe(
      map(response => (response?.success && response?.data)
        ? this.mapToDashboardManager(response.data)
        : null)
    );
  }

  getDashboardCommercial(): Observable<DashboardCommercial | null> {
    return this.getKPIsCommercial().pipe(
      map(response => (response?.success && response?.data)
        ? this.mapToDashboardCommercial(response.data)
        : null)
    );
  }

  getRapports(periode: string = 'mois'): Observable<any> {
    return this.http.get(`${this.baseUrl}/rapports/?periode=${periode}`).pipe(
      map(response => (response as any)?.data ?? response)
    );
  }

  private mapToDashboardManager(data: any): DashboardManager {
    const topPerformers = data.commerciaux?.top_performers || [];
    return {
      kpis: {
        commerciaux_actifs: data.commerciaux?.total || 0,
        clients_total: data.contacts?.total || data.clients?.total || 0,
        visites_jour: data.visites?.effectuees || 0,
        visites_mois: data.visites?.total || 0,
        commandes_jour: data.ventes?.total || 0,
        ca_mois: data.ventes?.montant_total || 0,
        taux_conversion: data.visites?.taux_conversion || 0,
        commerciaux_en_ligne: 0,
      },
      top_commerciaux: topPerformers.map((p: any) => ({
        id: p.id,
        nom: p.nom,
        matricule: p.matricule,
        ca_mois: p.total_ventes || 0,
        visites_mois: p.nombre_ventes || 0,
        taux_objectif: p.taux_objectif || 0,
      })),
      alertes: [],
    };
  }

  private mapToDashboardCommercial(data: any): DashboardCommercial {
    const commercial = data.commercial || {};
    const ventes = data.ventes || {};
    const visites = data.visites || {};
    const objectifMensuel = commercial.objectif_mensuel || 0;
    const montantAtteint = ventes.montant_total || 0;
    const tauxRealisation = ventes.progression_objectif || 0;

    return {
      commercial: {
        nom: commercial.nom || '',
        matricule: commercial.matricule || '',
        statut: 'ACTIF',
      },
      agenda_jour: [],
      objectifs: objectifMensuel > 0 ? [{
        periode: 'Mensuel',
        montant_cible: objectifMensuel,
        montant_atteint: montantAtteint,
        taux_realisation: tauxRealisation,
        is_atteint: tauxRealisation >= 100,
      }] : [],
      stats_mois: {
        ca: montantAtteint,
        visites: visites.effectuees || 0,
        distance_jour_km: 0,
        taux_objectif: tauxRealisation,
      },
    };
  }
}

export interface DashboardManager {
  kpis: {
    commerciaux_actifs: number;
    clients_total: number;
    visites_jour: number;
    visites_mois: number;
    commandes_jour: number;
    ca_mois: number;
    taux_conversion: number;
    commerciaux_en_ligne: number;
  };
  top_commerciaux: TopCommercial[];
  alertes: Alerte[];
}

export interface TopCommercial {
  id: number;
  nom: string;
  matricule: string;
  ca_mois: number;
  visites_mois: number;
  taux_objectif: number;
}

export interface Alerte {
  id: number;
  type: string;
  commercial: string;
  message: string;
  timestamp: string;
}

export interface DashboardCommercial {
  commercial: {
    nom: string;
    matricule: string;
    statut: string;
    zone?: string;
  };
  agenda_jour: AgendaItem[];
  objectifs: Objectif[];
  stats_mois: {
    ca: number;
    visites: number;
    distance_jour_km: number;
    taux_objectif: number;
  };
}

export interface AgendaItem {
  id: number;
  client: string;
  heure: string;
  statut: string;
  type: string;
  adresse: string;
  position?: { lat: number; lng: number } | null;
}

export interface Objectif {
  periode: string;
  montant_cible: number;
  montant_atteint: number;
  taux_realisation: number;
  is_atteint: boolean;
}

export interface RapportData {
  periode: string;
  date_debut: string;
  date_fin: string;
  visites_par_statut: any[];
  ca_par_jour: any[];
  visites_par_commercial: any[];
  opportunites_par_etape: any[];
}

export interface Visite {
  id: number;
  commercial: number;
  commercial_nom?: string;
  client: number;
  client_nom?: string;
  client_position?: { lat: number; lng: number } | null;
  type_visite: string;
  type_display?: string;
  date_prevue: string;
  date_effective?: string;
  duree_estimee: number;
  duree_reelle?: number;
  objectif?: string;
  statut: 'PLANIFIEE' | 'EN_COURS' | 'EFFECTUEE' | 'REPORTEE' | 'ANNULEE';
  statut_display?: string;
  is_validee?: boolean;
  checkin_lat?: number;
  checkin_lng?: number;
  checkin_timestamp?: string;
  checkout_lat?: number;
  checkout_lng?: number;
  checkout_timestamp?: string;
  compte_rendu?: string;
  actions_suivantes?: string;
  satisfaction_client?: number;
  distance_checkin?: number;
}

export interface CalendrierEvent {
  id: number;
  titre: string;
  date: string;
  statut: string;
  type: string;
  commercial: string;
  client: string;
}

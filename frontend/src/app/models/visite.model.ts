export interface Visite {
  id: number;
  manager: number;
  manager_nom?: string;
  point_vente_nom: string;
  contact_telephone?: string;
  quartier?: string;
  adresse_complete?: string;
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
  checkin_timestamp?: string;
  checkout_timestamp?: string;
  compte_rendu?: string;
  actions_suivantes?: string;
  note_controle?: number;
}

export interface CalendrierEvent {
  id: number;
  titre: string;
  date: string;
  statut: string;
  type: string;
  manager: string;
  point_vente: string;
}

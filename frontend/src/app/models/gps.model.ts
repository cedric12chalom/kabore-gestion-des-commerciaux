export interface PositionGPS {
  id: number;
  commercial: number;
  commercial_nom?: string;
  latitude: number;
  longitude: number;
  precision?: number;
  altitude?: number;
  vitesse?: number;
  cap?: number;
  source: string;
  timestamp: string;
}

export interface CommercialPosition {
  commercial_id: number;
  commercial_nom: string;
  matricule: string;
  lat: number;
  lng: number;
  vitesse?: number;
  precision?: number;
  timestamp: string;
  statut: string;
}

export interface ParcoursReplay {
  lat: number;
  lng: number;
  timestamp: string;
  vitesse?: number;
  precision?: number;
}

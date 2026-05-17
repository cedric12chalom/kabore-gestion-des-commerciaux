export interface Client {
  id: number;
  raison_sociale: string;
  nom_contact?: string;
  email?: string;
  telephone?: string;
  adresse: string;
  ville: string;
  code_postal?: string;
  pays: string;
  position?: any;
  latitude?: number;
  longitude?: number;
  secteur?: string;
  potentiel: 'A' | 'B' | 'C' | 'D';
  commercial_referent?: number;
  commercial_nom?: string;
  is_actif: boolean;
  nombre_visites?: number;
  ca_total?: number;
  notes?: string;
  date_creation: string;
  date_modification: string;
}

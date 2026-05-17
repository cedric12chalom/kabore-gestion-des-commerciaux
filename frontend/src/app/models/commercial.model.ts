export interface Commercial {
  id: number;
  matricule: string;
  nom_complet: string;
  email: string;
  telephones: Telephone[];
  statut: 'ACTIF' | 'CONGE' | 'SUSPENDU' | 'INACTIF';
  statut_display?: string;
  zone?: number | null;
  zone_nom?: string;
  objectif_mensuel: number;
  objectif_trimestriel: number;
  taux_objectif?: number;
  date_embauche?: string;
  vehicule?: string;
  immatriculation?: string;
  distance_jour?: number;
  nombre_visites_mois?: number;
  created_at: string;
  updated_at: string;
}

export interface Telephone {
  id: number;
  numero: string;
  type: 'MOBILE' | 'FIXE' | 'TRAVAIL' | 'WHATSAPP';
  type_display?: string;
  is_principal: boolean;
  is_whatsapp: boolean;
}

export interface Zone {
  id: number;
  nom: string;
  description: string;
  polygone?: any;
  manager: number;
  manager_nom?: string;
  ville: string;
  pays: string;
  is_active: boolean;
  surface_km2?: number;
  nombre_commerciaux?: number;
}

export interface Produit {
  id: number;
  reference: string;
  nom: string;
  description: string;
  categorie: string;
  categorie_display?: string;
  prix_unitaire: number;
  prix_gros?: number;
  stock: number;
  is_active: boolean;
  image?: string;
}

export interface Objectif {
  id: number;
  commercial: number;
  commercial_nom?: string;
  periode: string;
  type_objectif: string;
  valeur_cible: number;
  valeur_realisee?: number;
  taux_realisation?: number;
  date_debut: string;
  date_fin: string;
  statut?: string;
}

export interface Commande {
  id: number;
  reference: string;
  commercial: number;
  commercial_nom?: string;
  client: number;
  client_nom?: string;
  date: string;
  date_validation?: string;
  date_livraison_prevue?: string;
  montant_total: number;
  montant_remise: number;
  montant_ht: number;
  tva: number;
  montant_ttc?: number;
  statut: string;
  statut_display?: string;
  adresse_livraison?: string;
  notes?: string;
  lignes?: LigneCommande[];
  nombre_articles?: number;
}

export interface LigneCommande {
  id: number;
  produit: number;
  produit_nom?: string;
  produit_reference?: string;
  quantite: number;
  prix_unitaire: number;
  remise: number;
  montant_ligne: number;
}

export interface Opportunite {
  id: number;
  titre: string;
  description?: string;
  commercial: number;
  commercial_nom?: string;
  client: number;
  client_nom?: string;
  etape: string;
  etape_display?: string;
  probabilite: number;
  montant_estime: number;
  montant_final?: number;
  date_creation: string;
  date_cloture_prevue?: string;
  is_gagnee?: boolean;
  is_perdue?: boolean;
}

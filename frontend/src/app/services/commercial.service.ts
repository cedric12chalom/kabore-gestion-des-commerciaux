import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { Commercial, Zone, Produit, Objectif } from '../models/commercial.model';

@Injectable({
  providedIn: 'root'
})
export class CommercialService {
  private http = inject(HttpClient);
  private baseUrl = `${environment.apiUrl}/commerciaux`;

  getCommerciaux(params?: any): Observable<any> {
    let url = `${this.baseUrl}/`;
    if (params) {
      const query = new URLSearchParams(params).toString();
      url += `?${query}`;
    }
    return this.http.get(url);
  }

  getCommercial(id: number): Observable<any> {
    return this.http.get(`${this.baseUrl}/${id}/`);
  }

  createCommercial(data: any): Observable<any> {
    return this.http.post(`${this.baseUrl}/create/`, data);
  }

  updateCommercial(id: number, data: any): Observable<any> {
    return this.http.put(`${this.baseUrl}/${id}/`, data);
  }

  deleteCommercial(id: number): Observable<any> {
    return this.http.delete(`${this.baseUrl}/${id}/`);
  }

  getCommerciauxActifs(): Observable<any> {
    return this.http.get(`${this.baseUrl}/actifs/`);
  }

  getClientsProches(commercialId: number): Observable<any> {
    return this.http.get(`${this.baseUrl}/${commercialId}/clients-proches/`);
  }

  // Zones
  getZones(): Observable<any> {
    return this.http.get(`${this.baseUrl}/zones/`);
  }

  // Produits
  getProduits(): Observable<any> {
    return this.http.get(`${this.baseUrl}/produits/`);
  }

  // Objectifs
  getObjectifs(): Observable<any> {
    return this.http.get(`${this.baseUrl}/objectifs/`);
  }
}

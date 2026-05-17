import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class CommandeService {
  private http = inject(HttpClient);
  private baseUrl = `${environment.apiUrl}`;

  getCommandes(params?: any): Observable<any> {
    let url = `${this.baseUrl}/commandes/`;
    if (params) {
      const query = new URLSearchParams(params).toString();
      url += `?${query}`;
    }
    return this.http.get(url);
  }

  getCommande(id: number): Observable<any> {
    return this.http.get(`${this.baseUrl}/commandes/${id}/`);
  }

  createCommande(data: any): Observable<any> {
    return this.http.post(`${this.baseUrl}/commandes/`, data);
  }

  updateCommande(id: number, data: any): Observable<any> {
    return this.http.put(`${this.baseUrl}/commandes/${id}/`, data);
  }

  // Opportunités
  getOpportunites(params?: any): Observable<any> {
    let url = `${this.baseUrl}/commandes/opportunites/`;
    if (params) {
      const query = new URLSearchParams(params).toString();
      url += `?${query}`;
    }
    return this.http.get(url);
  }

  getPipelineStats(): Observable<any> {
    return this.http.get(`${this.baseUrl}/commandes/pipeline-stats/`);
  }
}

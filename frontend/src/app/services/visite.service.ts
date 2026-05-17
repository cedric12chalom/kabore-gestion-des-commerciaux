import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class VisiteService {
  private http = inject(HttpClient);
  private baseUrl = `${environment.apiUrl}/visites`;

  getVisites(params?: any): Observable<any> {
    let url = `${this.baseUrl}/`;
    if (params) {
      const query = new URLSearchParams(params).toString();
      url += `?${query}`;
    }
    return this.http.get(url);
  }

  getVisite(id: number): Observable<any> {
    return this.http.get(`${this.baseUrl}/${id}/`);
  }

  createVisite(data: any): Observable<any> {
    return this.http.post(`${this.baseUrl}/`, data);
  }

  updateVisite(id: number, data: any): Observable<any> {
    return this.http.put(`${this.baseUrl}/${id}/`, data);
  }

  checkin(visiteId: number, position: { latitude: number; longitude: number; precision?: number }): Observable<any> {
    return this.http.post(`${this.baseUrl}/${visiteId}/checkin/`, position);
  }

  checkout(visiteId: number, data: any): Observable<any> {
    return this.http.post(`${this.baseUrl}/${visiteId}/checkout/`, data);
  }

  getCalendrier(mois?: number, annee?: number): Observable<any> {
    let url = `${this.baseUrl}/calendrier/`;
    if (mois && annee) {
      url += `?mois=${mois}&annee=${annee}`;
    }
    return this.http.get(url);
  }
}

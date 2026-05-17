import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class ClientService {
  private http = inject(HttpClient);
  private baseUrl = `${environment.apiUrl}/clients`;

  getClients(params?: any): Observable<any> {
    let url = `${this.baseUrl}/`;
    if (params) {
      const query = new URLSearchParams(params).toString();
      url += `?${query}`;
    }
    return this.http.get(url);
  }

  getClient(id: number): Observable<any> {
    return this.http.get(`${this.baseUrl}/${id}/`);
  }

  createClient(data: any): Observable<any> {
    return this.http.post(`${this.baseUrl}/`, data);
  }

  updateClient(id: number, data: any): Observable<any> {
    return this.http.put(`${this.baseUrl}/${id}/`, data);
  }

  deleteClient(id: number): Observable<any> {
    return this.http.delete(`${this.baseUrl}/${id}/`);
  }
}

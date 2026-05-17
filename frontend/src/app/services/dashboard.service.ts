import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class DashboardService {
  private http = inject(HttpClient);
  private baseUrl = `${environment.apiUrl}/dashboard`;

  getDashboardManager(): Observable<any> {
    return this.http.get(`${this.baseUrl}/manager/`);
  }

  getDashboardCommercial(): Observable<any> {
    return this.http.get(`${this.baseUrl}/commercial/`);
  }

  getRapports(periode: string = 'mois'): Observable<any> {
    return this.http.get(`${this.baseUrl}/rapports/?periode=${periode}`);
  }
}

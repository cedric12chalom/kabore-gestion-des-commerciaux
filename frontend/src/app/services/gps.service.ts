import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, interval, Subject } from 'rxjs';
import { switchMap, takeUntil } from 'rxjs/operators';
import { environment } from '../../environments/environment';
import { PositionGPS, CommercialPosition, ParcoursReplay } from '../models/gps.model';

@Injectable({
  providedIn: 'root'
})
export class GpsService {
  private http = inject(HttpClient);
  private baseUrl = `${environment.apiUrl}/gps`;

  private stopPolling$ = new Subject<void>();

  // Envoyer une position GPS
  sendPosition(position: Partial<PositionGPS>): Observable<any> {
    return this.http.post(`${this.baseUrl}/positions/`, position);
  }

  // Récupérer les positions temps réel
  getPositionsTempsReel(): Observable<any> {
    return this.http.get(`${this.baseUrl}/temps-reel/`);
  }

  // Démarrer le polling GPS (toutes les 30 secondes)
  startGpsPolling(callback: (positions: CommercialPosition[]) => void): void {
    this.stopPolling();

    interval(environment.gpsUpdateInterval)
      .pipe(
        switchMap(() => this.getPositionsTempsReel()),
        takeUntil(this.stopPolling$)
      )
      .subscribe(response => {
        if (response.success) {
          callback(response.positions);
        }
      });
  }

  stopPolling(): void {
    this.stopPolling$.next();
    this.stopPolling$.complete();
    this.stopPolling$ = new Subject<void>();
  }

  // Replay d'un parcours
  getReplayParcours(commercialId: number, date: string): Observable<any> {
    return this.http.get(`${this.baseUrl}/replay/${commercialId}/?date=${date}`);
  }

  // Historique des parcours
  getHistoriqueParcours(params?: any): Observable<any> {
    let url = `${this.baseUrl}/parcours/`;
    if (params) {
      const query = new URLSearchParams(params).toString();
      url += `?${query}`;
    }
    return this.http.get(url);
  }

  // Synchronisation hors-ligne
  syncOfflinePositions(positions: any[]): Observable<any> {
    return this.http.post(`${this.baseUrl}/sync/`, { positions });
  }

  // Alertes zones
  getAlertes(): Observable<any> {
    return this.http.get(`${this.baseUrl}/alertes/`);
  }
}

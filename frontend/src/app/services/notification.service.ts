import { Injectable, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, interval, Observable } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class NotificationService {
  private http = inject(HttpClient);
  private baseUrl = `${environment.apiUrl}/notifications`;

  // Loading global
  private loadingSubject = new BehaviorSubject<boolean>(false);
  loading$ = this.loadingSubject.asObservable();

  // Compteur notifications
  unreadCount = signal<number>(0);

  private pollingInterval: any;

  setLoading(loading: boolean): void {
    this.loadingSubject.next(loading);
  }

  getNotifications(): Observable<any> {
    return this.http.get(`${this.baseUrl}/`);
  }

  getUnreadCount(): Observable<any> {
    return this.http.get(`${this.baseUrl}/non-lues/`);
  }

  markAsRead(notificationId: number): Observable<any> {
    return this.http.post(`${this.baseUrl}/${notificationId}/lue/`, {});
  }

  markAllAsRead(): Observable<any> {
    return this.http.post(`${this.baseUrl}/lues/`, {});
  }

  startPolling(): void {
    this.stopPolling();
    this.pollingInterval = setInterval(() => {
      this.getUnreadCount().subscribe(response => {
        if (response.success) {
          this.unreadCount.set(response.count);
        }
      });
    }, 60000); // Toutes les minutes
  }

  stopPolling(): void {
    if (this.pollingInterval) {
      clearInterval(this.pollingInterval);
    }
  }

  // Messages
  getMessages(): Observable<any> {
    return this.http.get(`${this.baseUrl}/messages/`);
  }

  getConversation(userId: number): Observable<any> {
    return this.http.get(`${this.baseUrl}/messages/${userId}/`);
  }

  sendMessage(data: { destinataire: number; contenu: string; client?: number; visite?: number }): Observable<any> {
    return this.http.post(`${this.baseUrl}/messages/`, data);
  }
}

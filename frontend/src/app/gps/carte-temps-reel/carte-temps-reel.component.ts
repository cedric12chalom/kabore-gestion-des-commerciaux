import {
  Component, inject, OnInit, OnDestroy,
  AfterViewInit, ElementRef, ViewChild, signal,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../environments/environment';
import { AuthService } from '../../services/auth.service';

declare const L: any;

interface PositionMarker {
  commercial_id: number;
  nom: string;
  matricule: string;
  lat: number;
  lng: number;
  online: boolean;
  accuracy?: number;
  timestamp: string;
}

@Component({
  selector: 'app-carte-temps-reel',
  standalone: true,
  imports: [CommonModule, MatCardModule, MatIconModule, MatChipsModule, MatProgressSpinnerModule],
  template: `
    <div class="carte-container">
      <div class="carte-header">
        <h2><mat-icon>my_location</mat-icon> Carte Temps Réel</h2>
        <mat-chip-set>
          <mat-chip>{{ stats().online }} en ligne</mat-chip>
          <mat-chip>{{ stats().offline }} hors ligne</mat-chip>
        </mat-chip-set>
      </div>
      <div class="carte-layout">
        <div class="map-wrapper">
          <div #mapEl class="map-el"></div>
          <div class="map-loading" *ngIf="loading()"><mat-spinner diameter="40"></mat-spinner></div>
        </div>
        <aside class="sidebar">
          <div class="commercial-row" *ngFor="let p of positions()"
               [class.offline]="!p.online" (click)="focusCommercial(p)">
            <span class="status-dot" [class.online]="p.online"></span>
            <div class="info"><strong>{{ p.nom }}</strong><small>{{ p.matricule }}</small></div>
            <small>{{ p.timestamp | date:'HH:mm:ss' }}</small>
          </div>
        </aside>
      </div>
    </div>
  `,
  styles: [`
    .carte-container { height: calc(100vh - 120px); display: flex; flex-direction: column; }
    .carte-header { display: flex; justify-content: space-between; align-items: center; padding: 0 0 16px; }
    .carte-layout { flex: 1; display: grid; grid-template-columns: 1fr 280px; gap: 16px; min-height: 0; }
    .map-wrapper { position: relative; border-radius: 12px; overflow: hidden; }
    .map-el { width: 100%; height: 100%; min-height: 400px; }
    .map-loading { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; background: rgba(255,255,255,.7); }
    .sidebar { overflow-y: auto; }
    .commercial-row { display: flex; align-items: center; gap: 10px; padding: 10px; border-radius: 8px; cursor: pointer; }
    .commercial-row:hover { background: #f0f4ff; }
    .commercial-row.offline { opacity: .6; }
    .status-dot { width: 10px; height: 10px; border-radius: 50%; background: #ea4335; }
    .status-dot.online { background: #34a853; }
    .info { flex: 1; display: flex; flex-direction: column; }
  `],
})
export class CarteTempsReelComponent implements OnInit, AfterViewInit, OnDestroy {
  @ViewChild('mapEl') mapEl!: ElementRef<HTMLDivElement>;

  private auth = inject(AuthService);
  private http = inject(HttpClient);
  private map: any;
  private markers = new Map<number, any>();
  private ws: WebSocket | null = null;
  private destroyed = false;

  loading = signal(true);
  positions = signal<PositionMarker[]>([]);
  stats = signal({ online: 0, offline: 0 });

  ngOnInit(): void {
    this.loadInitial();
    this.connectWatch();
  }

  ngAfterViewInit(): void {
    this.map = L.map(this.mapEl.nativeElement).setView([3.848, 11.502], 13);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(this.map);
  }

  ngOnDestroy(): void {
    this.destroyed = true;
    this.ws?.close();
    this.map?.remove();
  }

  focusCommercial(p: PositionMarker): void {
    this.map?.setView([p.lat, p.lng], 16);
    this.markers.get(p.commercial_id)?.openPopup();
  }

  private loadInitial(): void {
    this.http.get<any>(`${environment.apiUrl}/gps/positions-actuelles/`).subscribe({
      next: (res) => {
        this.updatePositions((res.data ?? []).map(this.normalize));
        this.loading.set(false);
      },
      error: () => this.loading.set(false),
    });
  }

  private connectWatch(): void {
    const token = this.auth.getAccessToken();
    if (!token) return;
    this.ws = new WebSocket(`${environment.wsUrl}/gps/watch/?token=${token}`);
    this.ws.onmessage = (e) => {
      const data = JSON.parse(e.data);
      if (data.commercial_id) {
        const updated = this.normalize(data);
        const list = [...this.positions()];
        const idx = list.findIndex(p => p.commercial_id === updated.commercial_id);
        if (idx >= 0) list[idx] = { ...list[idx], ...updated };
        else list.push(updated);
        this.updatePositions(list);
      }
    };
    this.ws.onclose = () => {
      if (!this.destroyed) setTimeout(() => this.connectWatch(), 5000);
    };
  }

  private updatePositions(items: PositionMarker[]): void {
    this.positions.set(items);
    this.stats.set({
      online: items.filter(p => p.online).length,
      offline: items.filter(p => !p.online).length,
    });
    items.forEach(p => this.upsertMarker(p));
    if (items.length && this.map) {
      const bounds = L.latLngBounds(items.map(p => [p.lat, p.lng]));
      this.map.fitBounds(bounds, { padding: [40, 40] });
    }
  }

  private upsertMarker(p: PositionMarker): void {
    const color = p.online ? '#34a853' : '#ea4335';
    const icon = L.divIcon({
      html: `<div style="width:14px;height:14px;border-radius:50%;background:${color};border:2px solid white"></div>`,
      iconSize: [14, 14], iconAnchor: [7, 7], className: '',
    });
    const popup = `<b>${p.nom}</b><br>${p.online ? 'En ligne' : 'Hors ligne'}`;
    const existing = this.markers.get(p.commercial_id);
    if (existing) {
      existing.setLatLng([p.lat, p.lng]);
      existing.setIcon(icon);
    } else {
      this.markers.set(p.commercial_id, L.marker([p.lat, p.lng], { icon }).addTo(this.map).bindPopup(popup));
    }
  }

  private normalize = (raw: any): PositionMarker => ({
    commercial_id: raw.commercial_id,
    nom: raw.nom ?? '—',
    matricule: raw.matricule ?? '',
    lat: raw.lat ?? raw.latitude ?? 0,
    lng: raw.lng ?? raw.longitude ?? 0,
    online: raw.online ?? true,
    accuracy: raw.accuracy,
    timestamp: raw.timestamp ?? new Date().toISOString(),
  });
}

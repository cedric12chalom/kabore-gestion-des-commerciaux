import { Component, inject, OnInit, OnDestroy, AfterViewInit, ElementRef, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { FormsModule } from '@angular/forms';
import { Subject, interval, takeUntil } from 'rxjs';
import { switchMap } from 'rxjs/operators';

import { GpsService } from '../../services/gps.service';
import { CommercialService } from '../../services/commercial.service';
import { AuthService } from '../../services/auth.service';
import { CommercialPosition } from '../../models/gps.model';

declare const L: any;

@Component({
  selector: 'app-carte-gps',
  standalone: true,
  imports: [
    CommonModule, MatCardModule, MatButtonModule, MatIconModule,
    MatChipsModule, MatSlideToggleModule, MatProgressSpinnerModule, FormsModule
  ],
  template: `
    <div class="carte-container">
      <div class="carte-header">
        <h2><mat-icon>map</mat-icon> Carte GPS Temps Réel</h2>
        <div class="carte-controls">
          <mat-chip-listbox>
            <mat-chip-option [selected]="autoRefresh" (click)="toggleAutoRefresh()">
              <mat-icon>sync</mat-icon> Auto-refresh
            </mat-chip-option>
            <mat-chip-option [selected]="showZones" (click)="toggleZones()">
              <mat-icon>terrain</mat-icon> Zones
            </mat-chip-option>
            <mat-chip-option [selected]="showHeatmap" (click)="toggleHeatmap()">
              <mat-icon>local_fire_department</mat-icon> Heatmap
            </mat-chip-option>
          </mat-chip-listbox>
        </div>
      </div>

      <div class="carte-layout">
        <!-- Carte Leaflet -->
        <div class="map-wrapper">
          <div #mapContainer class="map-container"></div>

          <div class="map-overlay" *ngIf="isLoading">
            <mat-spinner diameter="40"></mat-spinner>
            <span>Chargement de la carte...</span>
          </div>

          <!-- Légende -->
          <div class="map-legend">
            <div class="legend-item">
              <span class="legend-dot" style="background: #1a73e8;"></span>
              <span>En ligne</span>
            </div>
            <div class="legend-item">
              <span class="legend-dot" style="background: #ea4335;"></span>
              <span>Hors ligne</span>
            </div>
            <div class="legend-item">
              <span class="legend-dot" style="background: #fbbc04;"></span>
              <span>En visite</span>
            </div>
          </div>
        </div>

        <!-- Sidebar commerciaux -->
        <div class="commerciaux-panel">
          <h3>Commerciaux ({{ positions.length }})</h3>
          <div class="commerciaux-list">
            <div 
              class="commercial-card" 
              *ngFor="let pos of positions"
              [class.selected]="selectedCommercial === pos.commercial_id"
              (click)="focusOnCommercial(pos)">
              <div class="commercial-status" [class.online]="isOnline(pos)"></div>
              <div class="commercial-info">
                <span class="commercial-name">{{ pos.commercial_nom }}</span>
                <span class="commercial-matricule">{{ pos.matricule }}</span>
                <span class="commercial-details" *ngIf="pos.vitesse">
                  {{ pos.vitesse }} km/h
                </span>
              </div>
              <button mat-icon-button (click)="showRoute(pos); $event.stopPropagation()">
                <mat-icon>directions</mat-icon>
              </button>
            </div>
            <div class="empty-state" *ngIf="positions.length === 0">
              <mat-icon>person_off</mat-icon>
              <span>Aucun commercial actif</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .carte-container {
      height: calc(100vh - var(--header-height) - 48px);
      display: flex;
      flex-direction: column;
    }
    .carte-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 16px;
      flex-shrink: 0;
    }
    .carte-header h2 {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 20px;
      font-weight: 600;
      margin: 0;
    }
    .carte-controls {
      display: flex;
      gap: 8px;
    }
    .carte-layout {
      display: flex;
      flex: 1;
      gap: 16px;
      overflow: hidden;
    }
    .map-wrapper {
      flex: 1;
      position: relative;
      border-radius: 12px;
      overflow: hidden;
      box-shadow: var(--shadow-md);
    }
    .map-container {
      width: 100%;
      height: 100%;
    }
    .map-overlay {
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(255,255,255,0.8);
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 12px;
      z-index: 1000;
    }
    .map-legend {
      position: absolute;
      bottom: 20px;
      left: 20px;
      background: white;
      padding: 12px 16px;
      border-radius: 8px;
      box-shadow: var(--shadow-md);
      display: flex;
      flex-direction: column;
      gap: 8px;
      z-index: 500;
    }
    .legend-item {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 12px;
    }
    .legend-dot {
      width: 10px;
      height: 10px;
      border-radius: 50%;
    }
    .commerciaux-panel {
      width: 300px;
      background: white;
      border-radius: 12px;
      padding: 16px;
      box-shadow: var(--shadow-md);
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }
    .commerciaux-panel h3 {
      font-size: 16px;
      font-weight: 600;
      margin-bottom: 12px;
      flex-shrink: 0;
    }
    .commerciaux-list {
      flex: 1;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }
    .commercial-card {
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 12px;
      border-radius: 10px;
      cursor: pointer;
      transition: all 0.2s;
      border: 2px solid transparent;
    }
    .commercial-card:hover {
      background: var(--gray-100);
    }
    .commercial-card.selected {
      border-color: var(--primary);
      background: rgba(26, 115, 232, 0.05);
    }
    .commercial-status {
      width: 10px;
      height: 10px;
      border-radius: 50%;
      background: var(--gray-400);
      flex-shrink: 0;
    }
    .commercial-status.online {
      background: var(--success);
      animation: pulse 2s infinite;
    }
    .commercial-info {
      flex: 1;
      display: flex;
      flex-direction: column;
      min-width: 0;
    }
    .commercial-name {
      font-weight: 600;
      font-size: 13px;
    }
    .commercial-matricule {
      font-size: 11px;
      color: var(--gray-500);
    }
    .commercial-details {
      font-size: 11px;
      color: var(--gray-400);
    }
    .empty-state {
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 40px;
      color: var(--gray-400);
      gap: 8px;
    }
    @media (max-width: 768px) {
      .carte-layout {
        flex-direction: column;
      }
      .commerciaux-panel {
        width: 100%;
        height: 200px;
      }
    }
  `]
})
export class CarteGpsComponent implements OnInit, OnDestroy, AfterViewInit {
  @ViewChild('mapContainer') mapContainer!: ElementRef;

  private gpsService = inject(GpsService);
  private commercialService = inject(CommercialService);
  private authService = inject(AuthService);

  private destroy$ = new Subject<void>();
  private map: any;
  private markers: { [key: number]: any } = {};

  positions: CommercialPosition[] = [];
  isLoading = true;
  autoRefresh = true;
  showZones = false;
  showHeatmap = false;
  selectedCommercial: number | null = null;

  ngOnInit() {
    this.loadPositions();

    if (this.autoRefresh) {
      this.startPolling();
    }
  }

  ngAfterViewInit() {
    this.initMap();
  }

  ngOnDestroy() {
    this.destroy$.next();
    this.destroy$.complete();
    if (this.map) {
      this.map.remove();
    }
  }

  initMap() {
    if (!this.mapContainer) return;

    // Centre sur Douala, Cameroun
    this.map = L.map(this.mapContainer.nativeElement).setView([4.0511, 9.7680], 13);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors',
      maxZoom: 19,
    }).addTo(this.map);

    this.isLoading = false;
  }

  loadPositions() {
    this.gpsService.getPositionsTempsReel()
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (response) => {
          if (response.success) {
            this.positions = response.positions;
            this.updateMarkers();
          }
        }
      });
  }

  startPolling() {
    interval(30000)
      .pipe(
        switchMap(() => this.gpsService.getPositionsTempsReel()),
        takeUntil(this.destroy$)
      )
      .subscribe(response => {
        if (response.success) {
          this.positions = response.positions;
          this.updateMarkers();
        }
      });
  }

  updateMarkers() {
    if (!this.map) return;

    // Supprimer les anciens marqueurs
    Object.values(this.markers).forEach((marker: any) => this.map.removeLayer(marker));
    this.markers = {};

    // Ajouter les nouveaux marqueurs
    this.positions.forEach(pos => {
      const color = this.getMarkerColor(pos);
      const customIcon = L.divIcon({
        className: 'custom-marker',
        html: `<div style="
          background: ${color};
          width: 36px;
          height: 36px;
          border-radius: 50%;
          border: 3px solid white;
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
          font-weight: 600;
          font-size: 12px;
          box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        ">${pos.commercial_nom.charAt(0)}</div>`,
        iconSize: [36, 36],
        iconAnchor: [18, 18],
      });

      const marker = L.marker([pos.lat, pos.lng], { icon: customIcon })
        .addTo(this.map)
        .bindPopup(`
          <div style="font-family: Inter, sans-serif; min-width: 200px;">
            <h3 style="margin: 0 0 8px; font-size: 16px;">${pos.commercial_nom}</h3>
            <p style="margin: 4px 0; font-size: 13px; color: #666;">${pos.matricule}</p>
            <p style="margin: 4px 0; font-size: 12px;">
              <strong>Vitesse:</strong> ${pos.vitesse || 0} km/h
            </p>
            <p style="margin: 4px 0; font-size: 12px;">
              <strong>Dernière mise à jour:</strong> ${new Date(pos.timestamp).toLocaleTimeString()}
            </p>
          </div>
        `);

      this.markers[pos.commercial_id] = marker;
    });

    // Ajuster la vue pour voir tous les marqueurs
    if (this.positions.length > 0) {
      const group = new L.featureGroup(Object.values(this.markers));
      this.map.fitBounds(group.getBounds().pad(0.1));
    }
  }

  focusOnCommercial(pos: CommercialPosition) {
    this.selectedCommercial = pos.commercial_id;
    if (this.map) {
      this.map.setView([pos.lat, pos.lng], 16);
      const marker = this.markers[pos.commercial_id];
      if (marker) marker.openPopup();
    }
  }

  showRoute(pos: CommercialPosition) {
    // Ouvrir l'historique de parcours
    // Navigation vers la page historique
  }

  isOnline(pos: CommercialPosition): boolean {
    const lastUpdate = new Date(pos.timestamp);
    const now = new Date();
    return (now.getTime() - lastUpdate.getTime()) < 5 * 60 * 1000; // 5 minutes
  }

  getMarkerColor(pos: CommercialPosition): string {
    if (!this.isOnline(pos)) return '#ea4335'; // Rouge = hors ligne
    if (pos.statut === 'EN_COURS') return '#fbbc04'; // Jaune = en visite
    return '#1a73e8'; // Bleu = en ligne
  }

  toggleAutoRefresh() {
    this.autoRefresh = !this.autoRefresh;
    if (this.autoRefresh) {
      this.startPolling();
    }
  }

  toggleZones() {
    this.showZones = !this.showZones;
    // Afficher/masquer les polygones de zone
  }

  toggleHeatmap() {
    this.showHeatmap = !this.showHeatmap;
    // Activer/désactiver le heatmap
  }
}

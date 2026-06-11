import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterModule, Router } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { ClientService } from '../../services/client.service';

@Component({
  selector: 'app-client-detail',
  standalone: true,
  imports: [CommonModule, RouterModule, MatCardModule, MatButtonModule, MatIconModule, MatProgressSpinnerModule],
  template: `
    <div class="page-container" *ngIf="client; else loading">
      <div class="page-header">
        <div class="header-left">
          <button mat-icon-button routerLink="/clients">
            <mat-icon>arrow_back</mat-icon>
          </button>
          <div>
            <h1>{{ client.raison_sociale }}</h1>
            <span class="subtitle">{{ client.ville }} | Potentiel {{ client.potentiel }}</span>
          </div>
        </div>
        <button mat-raised-button color="primary" (click)="goToEdit()">
          <mat-icon>edit</mat-icon> Modifier
        </button>
      </div>

      <div class="detail-grid">
        <mat-card class="info-card">
          <h3>Informations</h3>
          <div class="info-row">
            <span class="label">Contact</span>
            <span class="value">{{ client.nom_contact || '-' }}</span>
          </div>
          <div class="info-row">
            <span class="label">Email</span>
            <span class="value">{{ client.email || '-' }}</span>
          </div>
          <div class="info-row">
            <span class="label">Téléphone</span>
            <span class="value">{{ client.telephone || '-' }}</span>
          </div>
          <div class="info-row">
            <span class="label">Adresse</span>
            <span class="value">{{ client.adresse }}</span>
          </div>
          <div class="info-row">
            <span class="label">Secteur</span>
            <span class="value">{{ client.secteur || '-' }}</span>
          </div>
          <div class="info-row">
            <span class="label">Commercial référent</span>
            <span class="value">{{ client.commercial_nom || '-' }}</span>
          </div>
        </mat-card>

        <mat-card class="stats-card">
          <h3>Statistiques</h3>
          <div class="stats-grid">
            <div class="stat-box">
              <mat-icon>event_note</mat-icon>
              <span class="stat-number">{{ client.nombre_visites || 0 }}</span>
              <span class="stat-label">Visites</span>
            </div>
            <div class="stat-box">
              <mat-icon>payments</mat-icon>
              <span class="stat-number">{{ client.ca_total | currency:'FCFA':'symbol':'1.0-0' }}</span>
              <span class="stat-label">CA Total</span>
            </div>
          </div>
        </mat-card>

        <mat-card class="map-card" *ngIf="client.latitude && client.longitude">
          <h3>Localisation</h3>
          <div class="coordinates">
            <span>Lat: {{ client.latitude }}</span>
            <span>Lng: {{ client.longitude }}</span>
          </div>
        </mat-card>
      </div>
    </div>

    <ng-template #loading>
      <div class="loading-overlay">
        <mat-spinner diameter="50"></mat-spinner>
      </div>
    </ng-template>
  `,
  styles: [`
    .page-container { padding: 0; }
    .page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
    .header-left { display: flex; align-items: center; gap: 16px; }
    .page-header h1 { margin: 0; font-size: 24px; }
    .subtitle { color: var(--gray-500); font-size: 14px; }
    .detail-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 20px; }
    .info-card, .stats-card, .map-card { padding: 24px; border-radius: 12px; }
    .info-card h3, .stats-card h3, .map-card h3 { font-size: 16px; font-weight: 600; margin-bottom: 16px; }
    .info-row { display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid var(--gray-100); }
    .info-row .label { color: var(--gray-500); font-size: 14px; }
    .info-row .value { font-weight: 500; font-size: 14px; }
    .stats-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; }
    .stat-box { display: flex; flex-direction: column; align-items: center; text-align: center; padding: 16px; background: var(--gray-100); border-radius: 10px; }
    .stat-box mat-icon { color: var(--primary); margin-bottom: 8px; }
    .stat-number { font-size: 18px; font-weight: 700; }
    .stat-label { font-size: 12px; color: var(--gray-500); }
    .coordinates { display: flex; gap: 16px; font-size: 13px; color: var(--gray-500); }
    .loading-overlay { display: flex; justify-content: center; padding: 60px; }
  `]
})
export class ClientDetailComponent {
  private route = inject(ActivatedRoute);
  private clientService = inject(ClientService);
  private router = inject(Router);

  client: any = null;

  constructor() {
    const id = Number(this.route.snapshot.paramMap.get('id'));
    this.loadClient(id);
  }

  loadClient(id: number) {
    this.clientService.getClient(id).subscribe({
      next: (response) => { this.client = response; }
    });
  }

  goToEdit(): void {
    this.router.navigate(['/clients', this.client?.id, 'edit']);
  }
}

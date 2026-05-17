import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterModule } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { CommercialService } from '../../services/commercial.service';

@Component({
  selector: 'app-commercial-detail',
  standalone: true,
  imports: [CommonModule, RouterModule, MatCardModule, MatButtonModule, MatIconModule, MatChipsModule, MatProgressSpinnerModule],
  template: `
    <div class="page-container" *ngIf="commercial; else loading">
      <div class="page-header">
        <div class="header-left">
          <button mat-icon-button routerLink="/commerciaux">
            <mat-icon>arrow_back</mat-icon>
          </button>
          <div>
            <h1>{{ commercial.nom_complet }}</h1>
            <span class="subtitle">{{ commercial.matricule }} | {{ commercial.statut_display }}</span>
          </div>
        </div>
        <button mat-raised-button color="primary">
          <mat-icon>edit</mat-icon> Modifier
        </button>
      </div>

      <div class="detail-grid">
        <mat-card class="info-card">
          <h3>Informations</h3>
          <div class="info-row">
            <span class="label">Email</span>
            <span class="value">{{ commercial.email }}</span>
          </div>
          <div class="info-row">
            <span class="label">Zone</span>
            <span class="value">{{ commercial.zone_nom || 'Non assignée' }}</span>
          </div>
          <div class="info-row">
            <span class="label">Objectif mensuel</span>
            <span class="value">{{ commercial.objectif_mensuel | currency:'FCFA':'symbol':'1.0-0' }}</span>
          </div>
          <div class="info-row">
            <span class="label">Taux objectif</span>
            <span class="value">{{ commercial.taux_objectif }}%</span>
          </div>
          <div class="info-row">
            <span class="label">Véhicule</span>
            <span class="value">{{ commercial.vehicule || '-' }}</span>
          </div>
        </mat-card>

        <mat-card class="stats-card">
          <h3>Statistiques</h3>
          <div class="stats-grid">
            <div class="stat-box">
              <mat-icon>event_note</mat-icon>
              <span class="stat-number">{{ commercial.nombre_visites_mois || 0 }}</span>
              <span class="stat-label">Visites ce mois</span>
            </div>
            <div class="stat-box">
              <mat-icon>payments</mat-icon>
              <span class="stat-number">{{ commercial.total_ventes | currency:'FCFA':'symbol':'1.0-0' }}</span>
              <span class="stat-label">Total ventes</span>
            </div>
            <div class="stat-box">
              <mat-icon>directions_walk</mat-icon>
              <span class="stat-number">{{ commercial.distance_jour || 0 }} km</span>
              <span class="stat-label">Distance aujourd'hui</span>
            </div>
          </div>
        </mat-card>

        <mat-card class="phones-card">
          <h3>Téléphones</h3>
          <div class="phone-list">
            <div class="phone-item" *ngFor="let tel of commercial.telephones">
              <mat-icon>{{ tel.is_whatsapp ? 'chat' : 'phone' }}</mat-icon>
              <div class="phone-info">
                <span class="phone-number">{{ tel.numero }}</span>
                <span class="phone-type">{{ tel.type_display }}</span>
              </div>
              <mat-chip *ngIf="tel.is_principal" color="primary" selected>Principal</mat-chip>
            </div>
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
    .page-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 24px;
    }
    .header-left { display: flex; align-items: center; gap: 16px; }
    .page-header h1 { margin: 0; font-size: 24px; }
    .subtitle { color: var(--gray-500); font-size: 14px; }
    .detail-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
      gap: 20px;
    }
    .info-card, .stats-card, .phones-card { padding: 24px; border-radius: 12px; }
    .info-card h3, .stats-card h3, .phones-card h3 { font-size: 16px; font-weight: 600; margin-bottom: 16px; }
    .info-row {
      display: flex;
      justify-content: space-between;
      padding: 12px 0;
      border-bottom: 1px solid var(--gray-100);
    }
    .info-row .label { color: var(--gray-500); font-size: 14px; }
    .info-row .value { font-weight: 500; font-size: 14px; }
    .stats-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 16px;
    }
    .stat-box {
      display: flex;
      flex-direction: column;
      align-items: center;
      text-align: center;
      padding: 16px;
      background: var(--gray-100);
      border-radius: 10px;
    }
    .stat-box mat-icon { color: var(--primary); margin-bottom: 8px; }
    .stat-number { font-size: 18px; font-weight: 700; }
    .stat-label { font-size: 12px; color: var(--gray-500); }
    .phone-list { display: flex; flex-direction: column; gap: 12px; }
    .phone-item {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 12px;
      background: var(--gray-100);
      border-radius: 10px;
    }
    .phone-info { flex: 1; display: flex; flex-direction: column; }
    .phone-number { font-weight: 600; }
    .phone-type { font-size: 12px; color: var(--gray-500); }
    .loading-overlay { display: flex; justify-content: center; padding: 60px; }
  `]
})
export class CommercialDetailComponent {
  private route = inject(ActivatedRoute);
  private commercialService = inject(CommercialService);

  commercial: any = null;

  constructor() {
    const id = Number(this.route.snapshot.paramMap.get('id'));
    this.loadCommercial(id);
  }

  loadCommercial(id: number) {
    this.commercialService.getCommercial(id).subscribe({
      next: (response) => {
        this.commercial = response;
      }
    });
  }
}

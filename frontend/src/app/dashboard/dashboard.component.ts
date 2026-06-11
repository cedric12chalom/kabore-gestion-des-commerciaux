import { Component, inject, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatChipsModule } from '@angular/material/chips';
import { RouterModule } from '@angular/router';
import { Subject, takeUntil } from 'rxjs';

import { AuthService } from '../services/auth.service';
import { DashboardService } from '../services/dashboard.service';
import { GpsService } from '../services/gps.service';
import { DashboardManager, DashboardCommercial, TopCommercial, Alerte } from '../models/dashboard.model';
import { CommercialPosition } from '../models/gps.model';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, MatCardModule, MatIconModule, MatButtonModule, MatProgressSpinnerModule, MatChipsModule, RouterModule],
  template: `
    <div class="dashboard-container">
      <!-- Loading -->
      <div class="loading-overlay" *ngIf="isLoading">
        <mat-spinner diameter="50"></mat-spinner>
      </div>

      <!-- DASHBOARD MANAGER / ADMIN -->
      <div *ngIf="isManagerOrAdmin() && managerData" class="dashboard-manager">
        <div class="kpi-grid">
          <mat-card class="kpi-card" *ngFor="let kpi of managerKpis">
            <div class="kpi-icon" [style.background]="kpi.color">
              <mat-icon>{{ kpi.icon }}</mat-icon>
            </div>
            <div class="kpi-content">
              <span class="kpi-value">{{ kpi.value }}</span>
              <span class="kpi-label">{{ kpi.label }}</span>
            </div>
          </mat-card>
        </div>

        <div class="dashboard-grid">
          <!-- Top commerciaux -->
          <mat-card class="dashboard-card">
            <mat-card-header>
              <mat-icon mat-card-avatar>emoji_events</mat-icon>
              <mat-card-title>Top Commerciaux</mat-card-title>
              <mat-card-subtitle>Ce mois</mat-card-subtitle>
            </mat-card-header>
            <mat-card-content>
              <div class="top-list">
                <div class="top-item" *ngFor="let com of managerData.top_commerciaux; let i = index">
                  <div class="top-rank">{{ i + 1 }}</div>
                  <div class="top-info">
                    <span class="top-name">{{ com.nom }}</span>
                    <span class="top-matricule">{{ com.matricule }}</span>
                  </div>
                  <div class="top-stats">
                    <span class="top-ca">{{ com.ca_mois | currency:'FCFA':'symbol':'1.0-0' }}</span>
                    <mat-chip [color]="com.taux_objectif >= 100 ? 'accent' : 'warn'" selected>
                      {{ com.taux_objectif }}%
                    </mat-chip>
                  </div>
                </div>
              </div>
            </mat-card-content>
          </mat-card>

          <!-- Alertes -->
          <mat-card class="dashboard-card">
            <mat-card-header>
              <mat-icon mat-card-avatar color="warn">warning</mat-icon>
              <mat-card-title>Alertes Récentes</mat-card-title>
            </mat-card-header>
            <mat-card-content>
              <div class="alertes-list">
                <div class="alerte-item" *ngFor="let alerte of managerData.alertes">
                  <mat-icon color="warn">warning_amber</mat-icon>
                  <div class="alerte-content">
                    <span class="alerte-commercial">{{ alerte.commercial }}</span>
                    <span class="alerte-message">{{ alerte.message }}</span>
                    <span class="alerte-time">{{ alerte.timestamp | date:'HH:mm' }}</span>
                  </div>
                </div>
                <div class="empty-state" *ngIf="managerData.alertes.length === 0">
                  <mat-icon>check_circle</mat-icon>
                  <span>Aucune alerte active</span>
                </div>
              </div>
            </mat-card-content>
          </mat-card>
        </div>
      </div>

      <!-- DASHBOARD COMMERCIAL -->
      <div *ngIf="isCommercial() && commercialData" class="dashboard-commercial">
        <div class="welcome-banner">
          <div class="welcome-content">
            <h2>Bonjour, {{ commercialData.commercial.nom }} !</h2>
            <p>Voici votre programme du jour</p>
          </div>
          <div class="welcome-stats">
            <div class="stat-item">
              <span class="stat-value">{{ commercialData.stats_mois.ca | currency:'FCFA':'symbol':'1.0-0' }}</span>
              <span class="stat-label">CA Mois</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{{ commercialData.stats_mois.visites }}</span>
              <span class="stat-label">Visites</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{{ commercialData.stats_mois.taux_objectif }}%</span>
              <span class="stat-label">Objectif</span>
            </div>
          </div>
        </div>

        <div class="agenda-section">
          <h3>Agenda du jour</h3>
          <div class="agenda-list">
            <mat-card class="agenda-card" *ngFor="let visite of commercialData.agenda_jour">
              <div class="agenda-time">{{ visite.heure }}</div>
              <div class="agenda-details">
                <span class="agenda-client">{{ visite.client }}</span>
                <span class="agenda-type">{{ visite.type }}</span>
                <span class="agenda-adresse">{{ visite.adresse }}</span>
              </div>
              <div class="agenda-status">
                <mat-chip [color]="getStatusColor(visite.statut)" selected>
                  {{ visite.statut }}
                </mat-chip>
              </div>
            </mat-card>
            <div class="empty-state" *ngIf="commercialData.agenda_jour.length === 0">
              <mat-icon>event_available</mat-icon>
              <span>Aucune visite planifiée aujourd'hui</span>
            </div>
          </div>
        </div>

        <!-- Objectifs -->
        <div class="objectifs-section" *ngIf="commercialData.objectifs.length > 0">
          <h3>Mes Objectifs</h3>
          <div class="objectifs-list">
            <div class="objectif-item" *ngFor="let obj of commercialData.objectifs">
              <div class="objectif-header">
                <span class="objectif-periode">{{ obj.periode }}</span>
                <span class="objectif-taux" [class.atteint]="obj.is_atteint">
                  {{ obj.taux_realisation }}%
                </span>
              </div>
              <div class="progress-bar">
                <div class="progress-fill" [style.width.%]="Math.min(obj.taux_realisation, 100)"></div>
              </div>
              <div class="objectif-montants">
                <span>{{ obj.montant_atteint | currency:'FCFA':'symbol':'1.0-0' }}</span>
                <span>/ {{ obj.montant_cible | currency:'FCFA':'symbol':'1.0-0' }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .dashboard-container {
      padding: 0;
    }
    .loading-overlay {
      display: flex;
      justify-content: center;
      padding: 60px;
    }

    /* KPI Grid */
    .kpi-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 20px;
      margin-bottom: 24px;
    }
    .kpi-card {
      display: flex;
      align-items: center;
      gap: 16px;
      padding: 20px;
      border-radius: 12px;
      transition: transform 0.2s, box-shadow 0.2s;
    }
    .kpi-card:hover {
      transform: translateY(-2px);
      box-shadow: var(--shadow-lg);
    }
    .kpi-icon {
      width: 48px;
      height: 48px;
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
      flex-shrink: 0;
    }
    .kpi-icon mat-icon {
      font-size: 24px;
      width: 24px;
      height: 24px;
    }
    .kpi-content {
      display: flex;
      flex-direction: column;
    }
    .kpi-value {
      font-size: 24px;
      font-weight: 700;
      color: var(--gray-900);
    }
    .kpi-label {
      font-size: 13px;
      color: var(--gray-500);
    }

    /* Dashboard Grid */
    .dashboard-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
      gap: 24px;
    }
    .dashboard-card {
      border-radius: 12px;
    }

    /* Top Commerciaux */
    .top-list {
      display: flex;
      flex-direction: column;
      gap: 12px;
    }
    .top-item {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 12px;
      background: var(--gray-100);
      border-radius: 10px;
    }
    .top-rank {
      width: 32px;
      height: 32px;
      background: var(--primary);
      color: white;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 700;
      font-size: 14px;
    }
    .top-info {
      flex: 1;
      display: flex;
      flex-direction: column;
    }
    .top-name {
      font-weight: 600;
      font-size: 14px;
    }
    .top-matricule {
      font-size: 12px;
      color: var(--gray-500);
    }
    .top-stats {
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .top-ca {
      font-weight: 600;
      color: var(--success);
    }

    /* Alertes */
    .alertes-list {
      display: flex;
      flex-direction: column;
      gap: 12px;
    }
    .alerte-item {
      display: flex;
      gap: 12px;
      padding: 12px;
      background: rgba(234, 67, 53, 0.05);
      border-radius: 10px;
      border-left: 3px solid var(--danger);
    }
    .alerte-content {
      display: flex;
      flex-direction: column;
      flex: 1;
    }
    .alerte-commercial {
      font-weight: 600;
      font-size: 13px;
    }
    .alerte-message {
      font-size: 12px;
      color: var(--gray-600);
    }
    .alerte-time {
      font-size: 11px;
      color: var(--gray-400);
    }

    /* Commercial Dashboard */
    .welcome-banner {
      background: linear-gradient(135deg, var(--primary), var(--primary-dark));
      border-radius: 16px;
      padding: 32px;
      color: white;
      margin-bottom: 24px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .welcome-content h2 {
      font-size: 24px;
      font-weight: 700;
      margin-bottom: 4px;
    }
    .welcome-content p {
      opacity: 0.9;
    }
    .welcome-stats {
      display: flex;
      gap: 32px;
    }
    .stat-item {
      display: flex;
      flex-direction: column;
      align-items: center;
      text-align: center;
    }
    .stat-value {
      font-size: 28px;
      font-weight: 700;
    }
    .stat-label {
      font-size: 12px;
      opacity: 0.8;
    }

    /* Agenda */
    .agenda-section, .objectifs-section {
      margin-bottom: 24px;
    }
    .agenda-section h3, .objectifs-section h3 {
      font-size: 18px;
      font-weight: 600;
      margin-bottom: 16px;
      color: var(--gray-800);
    }
    .agenda-list {
      display: flex;
      flex-direction: column;
      gap: 12px;
    }
    .agenda-card {
      display: flex;
      align-items: center;
      gap: 16px;
      padding: 16px;
      border-radius: 12px;
      transition: box-shadow 0.2s;
    }
    .agenda-card:hover {
      box-shadow: var(--shadow-md);
    }
    .agenda-time {
      font-size: 18px;
      font-weight: 700;
      color: var(--primary);
      min-width: 60px;
    }
    .agenda-details {
      flex: 1;
      display: flex;
      flex-direction: column;
    }
    .agenda-client {
      font-weight: 600;
      font-size: 15px;
    }
    .agenda-type {
      font-size: 13px;
      color: var(--gray-500);
    }
    .agenda-adresse {
      font-size: 12px;
      color: var(--gray-400);
    }

    /* Objectifs */
    .objectifs-list {
      display: flex;
      flex-direction: column;
      gap: 16px;
    }
    .objectif-item {
      background: var(--white);
      padding: 20px;
      border-radius: 12px;
      box-shadow: var(--shadow-sm);
    }
    .objectif-header {
      display: flex;
      justify-content: space-between;
      margin-bottom: 12px;
    }
    .objectif-periode {
      font-weight: 600;
      color: var(--gray-700);
    }
    .objectif-taux {
      font-weight: 700;
      color: var(--warning);
    }
    .objectif-taux.atteint {
      color: var(--success);
    }
    .progress-bar {
      height: 8px;
      background: var(--gray-200);
      border-radius: 4px;
      overflow: hidden;
      margin-bottom: 8px;
    }
    .progress-fill {
      height: 100%;
      background: linear-gradient(90deg, var(--primary), var(--success));
      border-radius: 4px;
      transition: width 0.5s ease;
    }
    .objectif-montants {
      display: flex;
      justify-content: space-between;
      font-size: 13px;
      color: var(--gray-500);
    }

    /* Empty state */
    .empty-state {
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 40px;
      color: var(--gray-400);
      gap: 8px;
    }
    .empty-state mat-icon {
      font-size: 48px;
      width: 48px;
      height: 48px;
    }
  `]
})
export class DashboardComponent implements OnInit, OnDestroy {
  private authService = inject(AuthService);
  private dashboardService = inject(DashboardService);
  private gpsService = inject(GpsService);

  private destroy$ = new Subject<void>();

  isLoading = true;
  managerData: DashboardManager | null = null;
  commercialData: DashboardCommercial | null = null;

  Math = Math;

  ngOnInit() {
    this.loadDashboard();
  }

  ngOnDestroy() {
    this.destroy$.next();
    this.destroy$.complete();
  }

  loadDashboard() {
    this.isLoading = true;

    if (this.isManagerOrAdmin()) {
      this.dashboardService.getDashboardManager()
        .pipe(takeUntil(this.destroy$))
        .subscribe({
          next: (data) => {
            this.managerData = data;
            this.isLoading = false;
          },
          error: () => {
            this.isLoading = false;
          }
        });
    } else {
      this.dashboardService.getDashboardCommercial()
        .pipe(takeUntil(this.destroy$))
        .subscribe({
          next: (data) => {
            this.commercialData = data;
            this.isLoading = false;
          },
          error: () => {
            this.isLoading = false;
          }
        });
    }
  }

  get managerKpis() {
    if (!this.managerData) return [];
    const k = this.managerData.kpis;
    return [
      { label: 'Commerciaux Actifs', value: k.commerciaux_actifs, icon: 'people', color: 'linear-gradient(135deg, #667eea, #764ba2)' },
      { label: 'Clients', value: k.clients_total, icon: 'business', color: 'linear-gradient(135deg, #f093fb, #f5576c)' },
      { label: "Visites Aujourd'hui", value: k.visites_jour, icon: 'event_note', color: 'linear-gradient(135deg, #4facfe, #00f2fe)' },
      { label: 'CA du Mois', value: (k.ca_mois / 1000000).toFixed(1) + 'M FCFA', icon: 'payments', color: 'linear-gradient(135deg, #43e97b, #38f9d7)' },
      { label: 'Taux Conversion', value: k.taux_conversion + '%', icon: 'trending_up', color: 'linear-gradient(135deg, #fa709a, #fee140)' },
      { label: 'En Ligne', value: k.commerciaux_en_ligne, icon: 'online_prediction', color: 'linear-gradient(135deg, #30cfd0, #330867)' },
    ];
  }

  isManagerOrAdmin(): boolean {
    return this.authService.isAdmin() || this.authService.isManager();
  }

  isCommercial(): boolean {
    return this.authService.isCommercial();
  }

  getStatusColor(statut: string): string {
    const colors: { [key: string]: string } = {
      'PLANIFIEE': 'primary',
      'EN_COURS': 'accent',
      'EFFECTUEE': 'primary',
      'REPORTEE': 'warn',
      'ANNULEE': 'warn',
    };
    return colors[statut] || 'primary';
  }
}

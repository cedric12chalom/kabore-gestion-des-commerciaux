import { Component, inject, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatSelectModule } from '@angular/material/select';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBar } from '@angular/material/snack-bar';
import { FormsModule } from '@angular/forms';
import { BaseChartDirective } from 'ng2-charts';
import { ChartConfiguration } from 'chart.js';
import { DashboardService } from '../services/dashboard.service';
import { AuthService } from '../services/auth.service';

interface KPICard {
  title: string;
  value: string | number;
  subtitle?: string;
  color: 'primary' | 'accent' | 'warn';
}

@Component({
  selector: 'app-rapports',
  standalone: true,
  imports: [
    CommonModule, MatCardModule, MatButtonModule, MatIconModule,
    MatSelectModule, MatFormFieldModule, MatProgressBarModule,
    MatProgressSpinnerModule, FormsModule, BaseChartDirective
  ],
  template: `
    <div class="rapports-container">
      <div class="rapports-header">
        <h1>Rapports & Analytics</h1>
        <div class="header-controls">
          <mat-form-field appearance="outline" class="period-select">
            <mat-label>Période</mat-label>
            <mat-select [(ngModel)]="periode" (selectionChange)="loadKPIs()">
              <mat-option value="">Période personnalisée</mat-option>
              <mat-option value="jour">Aujourd'hui</mat-option>
              <mat-option value="semaine">Cette semaine</mat-option>
              <mat-option value="mois">Ce mois</mat-option>
              <mat-option value="trimestre">Ce trimestre</mat-option>
              <mat-option value="annee">Cette année</mat-option>
            </mat-select>
          </mat-form-field>
          <button mat-raised-button color="primary" (click)="exportCSV()">
            <mat-icon>download</mat-icon> CSV
          </button>
        </div>
      </div>

      <!-- KPI Cards -->
      <div class="kpi-grid" *ngIf="kpis()">
        <mat-card class="kpi-card" *ngFor="let kpi of getKPICards()">
          <div class="kpi-content">
            <h3 class="kpi-title">{{ kpi.title }}</h3>
            <div class="kpi-value">{{ formatValue(kpi.value) }}</div>
            <p class="kpi-subtitle" *ngIf="kpi.subtitle">{{ kpi.subtitle }}</p>
          </div>
        </mat-card>
      </div>

      <!-- Charts Grid -->
      <div class="charts-grid">
        <!-- Evolution Ventes -->
        <mat-card class="chart-card" *ngIf="evolutionChartData.datasets">
          <h3>Évolution des Ventes</h3>
          <canvas baseChart
            [data]="evolutionChartData"
            [options]="lineChartOptions"
            [type]="'line'">
          </canvas>
        </mat-card>

        <!-- Statut Visites -->
        <mat-card class="chart-card" *ngIf="visitesChartData.datasets">
          <h3>Statut des Visites</h3>
          <canvas baseChart
            [data]="visitesChartData"
            [options]="doughnutChartOptions"
            [type]="'doughnut'">
          </canvas>
        </mat-card>
      </div>

      <!-- Top Performer & Objectifs -->
      <div class="bottom-grid">
        <!-- Top Performers -->
        <mat-card class="performers-card" *ngIf="kpis()?.commerciaux?.top_performers">
          <h3>Top Performers</h3>
          <div class="performers-list">
            <div class="performer-item" *ngFor="let performer of kpis()!.commerciaux.top_performers; let i = index">
              <div class="performer-rank">{{ i + 1 }}</div>
              <div class="performer-info">
                <div class="performer-name">{{ performer.nom }}</div>
                <div class="performer-detail">{{ performer.matricule }}</div>
              </div>
              <div class="performer-stats">
                <div class="stat">{{ performer.nombre_ventes }} ventes</div>
                <div class="stat-amount">{{ formatCurrency(performer.total_ventes) }} FCFA</div>
              </div>
            </div>
          </div>
        </mat-card>

        <!-- Objectifs -->
        <mat-card class="objectifs-card" *ngIf="kpis()?.commerciaux?.objectifs_atteints">
          <h3>Objectifs Mensuels</h3>
          <div class="objectif-item">
            <div class="objectif-label">
              <span>Taux réalisation</span>
              <span class="objectif-value">{{ kpis()!.commerciaux.objectifs_atteints.taux }}%</span>
            </div>
            <mat-progress-bar 
              mode="determinate" 
              [value]="kpis()!.commerciaux.objectifs_atteints.taux">
            </mat-progress-bar>
            <div class="objectif-detail">
              {{ kpis()!.commerciaux.objectifs_atteints.atteints }} / {{ kpis()!.commerciaux.objectifs_atteints.total }} objectifs atteints
            </div>
          </div>
        </mat-card>
      </div>

      <!-- Loading State -->
      <div class="loading" *ngIf="isLoading()">
        <mat-spinner></mat-spinner>
      </div>
    </div>
  `,
  styles: [`
    .rapports-container { padding: 24px; max-width: 1400px; margin: 0 auto; }
    .rapports-header { 
      display: flex; 
      justify-content: space-between; 
      align-items: center; 
      margin-bottom: 32px;
      gap: 24px;
    }
    .rapports-header h1 { font-size: 28px; font-weight: 600; margin: 0; }
    .header-controls { display: flex; gap: 16px; align-items: flex-end; }
    .period-select { width: 180px; }

    /* KPI Grid */
    .kpi-grid { 
      display: grid; 
      grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); 
      gap: 16px; 
      margin-bottom: 32px;
    }
    .kpi-card { 
      padding: 20px;
      border-left: 4px solid var(--primary);
      cursor: pointer;
      transition: transform 0.2s, box-shadow 0.2s;
    }
    .kpi-card:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
    .kpi-content { }
    .kpi-title { 
      font-size: 12px; 
      font-weight: 500; 
      color: #666;
      text-transform: uppercase;
      margin: 0 0 12px 0;
      letter-spacing: 0.5px;
    }
    .kpi-value { 
      font-size: 32px; 
      font-weight: 700; 
      color: var(--primary);
      margin: 0 0 8px 0;
    }
    .kpi-subtitle { 
      font-size: 12px; 
      color: #999; 
      margin: 0;
    }

    /* Charts Grid */
    .charts-grid { 
      display: grid; 
      grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); 
      gap: 24px; 
      margin-bottom: 32px;
    }
    .chart-card { padding: 24px; }
    .chart-card h3 { font-size: 16px; font-weight: 600; margin: 0 0 16px 0; }

    /* Bottom Grid */
    .bottom-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 24px; }
    
    .performers-card, .objectifs-card { padding: 24px; }
    .performers-card h3, .objectifs-card h3 { font-size: 16px; font-weight: 600; margin: 0 0 16px 0; }

    /* Performers List */
    .performers-list { display: flex; flex-direction: column; gap: 12px; }
    .performer-item { 
      display: flex; 
      align-items: center; 
      gap: 12px; 
      padding: 12px; 
      background: #f5f5f5; 
      border-radius: 8px;
    }
    .performer-rank { 
      width: 32px; 
      height: 32px; 
      border-radius: 50%; 
      background: var(--primary); 
      color: white; 
      display: flex; 
      align-items: center; 
      justify-content: center; 
      font-weight: 700; 
      font-size: 14px;
    }
    .performer-info { flex: 1; }
    .performer-name { font-weight: 600; font-size: 14px; }
    .performer-detail { font-size: 12px; color: #666; }
    .performer-stats { text-align: right; }
    .stat { font-size: 12px; color: #666; }
    .stat-amount { font-weight: 600; color: var(--primary); font-size: 14px; }

    /* Objectifs */
    .objectif-item { }
    .objectif-label { display: flex; justify-content: space-between; margin-bottom: 8px; }
    .objectif-value { font-weight: 600; color: var(--primary); }
    .objectif-detail { font-size: 12px; color: #666; margin-top: 8px; }

    .loading { display: flex; justify-content: center; align-items: center; min-height: 400px; }

    @media (max-width: 768px) {
      .rapports-header { flex-direction: column; align-items: flex-start; }
      .header-controls { width: 100%; flex-direction: column; }
      .period-select { width: 100%; }
      .kpi-grid { grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); }
      .charts-grid { grid-template-columns: 1fr; }
    }
  `]
})
export class RapportsComponent implements OnInit {
  private dashboardService = inject(DashboardService);
  private authService = inject(AuthService);
  private snackBar = inject(MatSnackBar);

  periode = 'mois';
  isLoading = signal(false);
  kpis = signal<any>(null);

  evolutionChartData: ChartConfiguration<'line'>['data'] = { labels: [], datasets: [] };
  visitesChartData: ChartConfiguration<'doughnut'>['data'] = { labels: [], datasets: [] };

  lineChartOptions: ChartConfiguration<'line'>['options'] = {
    responsive: true,
    maintainAspectRatio: true,
    plugins: { legend: { position: 'bottom' as const } },
    scales: { y: { beginAtZero: true } }
  };

  doughnutChartOptions: ChartConfiguration<'doughnut'>['options'] = {
    responsive: true,
    maintainAspectRatio: true,
    plugins: { legend: { position: 'bottom' as const } }
  };


  ngOnInit() {
    this.loadKPIs();
  }

  loadKPIs() {
    this.isLoading.set(true);
    
    const dateDebut = this.periode ? this.calculateDateDebut() : undefined;
    const dateEnd = new Date().toISOString().split('T')[0];

    const request$ = this.authService.isCommercial()
      ? this.dashboardService.getKPIsCommercial(dateDebut, dateEnd)
      : this.dashboardService.getKPIsManager(dateDebut, dateEnd);

    request$.subscribe({
      next: (response) => {
        if (response.success && response.data) {
          this.kpis.set(response.data);
          this.updateCharts(response.data);
        }
        this.isLoading.set(false);
      },
      error: (err) => {
        console.error('Erreur chargement KPIs:', err);
        this.snackBar.open('Erreur lors du chargement des données', 'Fermer', { duration: 3000 });
        this.isLoading.set(false);
      }
    });
  }

  calculateDateDebut(): string {
    const today = new Date();
    const dateDebut = new Date();
    
    switch (this.periode) {
      case 'jour':
        // Aujourd'hui
        break;
      case 'semaine':
        dateDebut.setDate(today.getDate() - today.getDay());
        break;
      case 'mois':
        dateDebut.setDate(1);
        break;
      case 'trimestre':
        const trimestre = Math.floor(today.getMonth() / 3);
        dateDebut.setMonth(trimestre * 3, 1);
        break;
      case 'annee':
        dateDebut.setMonth(0, 1);
        break;
    }
    
    return dateDebut.toISOString().split('T')[0];
  }

  updateCharts(data: any) {
    // Evolution ventes
    if (data.ventes?.evolution) {
      this.evolutionChartData = {
        labels: data.ventes.evolution.map((e: any) => e.date),
        datasets: [{
          label: 'CA (FCFA)',
          data: data.ventes.evolution.map((e: any) => e.montant),
          borderColor: '#1a73e8',
          backgroundColor: 'rgba(26, 115, 232, 0.1)',
          tension: 0.3,
          fill: true
        }]
      };
    }

    // Visites par statut
    if (data.visites) {
      this.visitesChartData = {
        labels: ['Effectuées', 'Planifiées', 'Annulées'],
        datasets: [{
          data: [
            data.visites.effectuees || 0,
            data.visites.planifiees || 0,
            data.visites.annulees || 0
          ],
          backgroundColor: ['#34a853', '#fbbc04', '#ea4335']
        }]
      };
    }
  }

  getKPICards(): KPICard[] {
    if (!this.kpis()) return [];
    
    const data = this.kpis();
    return [
      {
        title: 'Ventes',
        value: data.ventes?.total || 0,
        subtitle: `${this.formatCurrency(data.ventes?.montant_total || 0)} FCFA`,
        color: 'primary'
      },
      {
        title: 'Visites Effectuées',
        value: data.visites?.effectuees || 0,
        subtitle: `Taux conversion: ${data.visites?.taux_conversion || 0}%`,
        color: 'accent'
      },
      {
        title: 'Commerciaux Actifs',
        value: data.commerciaux?.total || 0,
        subtitle: `Objectifs atteints: ${data.commerciaux?.objectifs_atteints?.atteints || 0}`,
        color: 'primary'
      },
      {
        title: 'Contacts',
        value: data.contacts?.total || data.clients?.total || 0,
        subtitle: `+${data.contacts?.nouveaux || data.clients?.nouveaux || 0} nouveaux`,
        color: 'accent'
      }
    ];
  }

  formatValue(value: string | number): string {
    if (typeof value === 'number' && value > 1000) {
      return (value / 1000).toFixed(1) + 'k';
    }
    return String(value);
  }

  formatCurrency(value: number): string {
    return new Intl.NumberFormat('fr-CM', {
      style: 'decimal',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value);
  }

  exportCSV() {
    this.isLoading.set(true);
    const dateDebut = this.periode ? this.calculateDateDebut() : undefined;
    const dateEnd = new Date().toISOString().split('T')[0];

    this.dashboardService.exporterRapport(dateDebut, dateEnd).subscribe({
      next: (blob) => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `rapport_${new Date().toISOString().split('T')[0]}.csv`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        this.snackBar.open('Export réussi!', 'Fermer', { duration: 2000 });
        this.isLoading.set(false);
      },
      error: (err) => {
        console.error('Erreur export:', err);
        this.snackBar.open('Erreur lors de l\'export', 'Fermer', { duration: 3000 });
        this.isLoading.set(false);
      }
    });
  }
}

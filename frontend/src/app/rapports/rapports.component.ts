import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatSelectModule } from '@angular/material/select';
import { MatFormFieldModule } from '@angular/material/form-field';
import { FormsModule } from '@angular/forms';
import { BaseChartDirective } from 'ng2-charts';
import { ChartConfiguration } from 'chart.js';
import { DashboardService } from '../services/dashboard.service';

@Component({
  selector: 'app-rapports',
  standalone: true,
  imports: [
    CommonModule, MatCardModule, MatButtonModule, MatIconModule,
    MatSelectModule, MatFormFieldModule, FormsModule, BaseChartDirective
  ],
  template: `
    <div class="rapports-container">
      <div class="rapports-header">
        <h1>Rapports & Analytics</h1>
        <mat-form-field appearance="outline">
          <mat-label>Période</mat-label>
          <mat-select [(ngModel)]="periode" (selectionChange)="loadRapports()">
            <mat-option value="jour">Aujourd'hui</mat-option>
            <mat-option value="semaine">Cette semaine</mat-option>
            <mat-option value="mois">Ce mois</mat-option>
            <mat-option value="trimestre">Ce trimestre</mat-option>
            <mat-option value="annee">Cette année</mat-option>
          </mat-select>
        </mat-form-field>
      </div>

      <div class="charts-grid">
        <mat-card class="chart-card">
          <h3>Visites par statut</h3>
          <canvas baseChart
            [data]="visitesChartData"
            [options]="chartOptions"
            [type]="'doughnut'">
          </canvas>
        </mat-card>

        <mat-card class="chart-card">
          <h3>CA par jour</h3>
          <canvas baseChart
            [data]="caChartData"
            [options]="chartOptions"
            [type]="'line'">
          </canvas>
        </mat-card>

        <mat-card class="chart-card">
          <h3>Opportunités par étape</h3>
          <canvas baseChart
            [data]="opportunitesChartData"
            [options]="chartOptions"
            [type]="'bar'">
          </canvas>
        </mat-card>

        <mat-card class="chart-card">
          <h3>Top Commerciaux</h3>
          <div class="top-list" *ngIf="rapportData">
            <div class="top-item" *ngFor="let com of rapportData.visites_par_commercial">
              <span class="top-name">{{ com.commercial__user__first_name }} {{ com.commercial__user__last_name }}</span>
              <span class="top-value">{{ com.count }} visites</span>
            </div>
          </div>
        </mat-card>
      </div>

      <div class="export-section">
        <button mat-raised-button color="primary" (click)="exportCSV()">
          <mat-icon>download</mat-icon> Exporter CSV
        </button>
        <button mat-raised-button color="accent" (click)="exportPDF()">
          <mat-icon>picture_as_pdf</mat-icon> Exporter PDF
        </button>
      </div>
    </div>
  `,
  styles: [`
    .rapports-container { padding: 0; }
    .rapports-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
    .rapports-header h1 { font-size: 24px; font-weight: 600; margin: 0; }
    .charts-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 24px; margin-bottom: 24px; }
    .chart-card { padding: 20px; }
    .chart-card h3 { font-size: 16px; font-weight: 600; margin-bottom: 16px; }
    .top-list { display: flex; flex-direction: column; gap: 12px; }
    .top-item { display: flex; justify-content: space-between; padding: 12px; background: var(--gray-100); border-radius: 8px; }
    .top-name { font-weight: 500; }
    .top-value { color: var(--primary); font-weight: 600; }
    .export-section { display: flex; gap: 12px; justify-content: flex-end; }
  `]
})
export class RapportsComponent implements OnInit {
  private dashboardService = inject(DashboardService);

  periode = 'mois';
  rapportData: any = null;

  visitesChartData: ChartConfiguration<'doughnut'>['data'] = {
    labels: [],
    datasets: [{ data: [], backgroundColor: ['#34a853', '#fbbc04', '#ea4335', '#9aa0a6'] }]
  };

  caChartData: ChartConfiguration<'line'>['data'] = {
    labels: [],
    datasets: [{ data: [], label: 'CA (FCFA)', borderColor: '#1a73e8', tension: 0.4 }]
  };

  opportunitesChartData: ChartConfiguration<'bar'>['data'] = {
    labels: [],
    datasets: [{ data: [], label: 'Opportunités', backgroundColor: '#1a73e8' }]
  };

  chartOptions = {
    responsive: true,
    plugins: { legend: { position: 'bottom' as const } }
  };

  ngOnInit() {
    this.loadRapports();
  }

  loadRapports() {
    this.dashboardService.getRapports(this.periode).subscribe({
      next: (response) => {
        if (response.success) {
          this.rapportData = response;
          this.updateCharts(response);
        }
      }
    });
  }

  updateCharts(data: any) {
    this.visitesChartData.labels = data.visites_par_statut.map((v: any) => v.statut);
    this.visitesChartData.datasets[0].data = data.visites_par_statut.map((v: any) => v.count);

    this.caChartData.labels = data.ca_par_jour.map((c: any) => c.date__date);
    this.caChartData.datasets[0].data = data.ca_par_jour.map((c: any) => c.ca);

    this.opportunitesChartData.labels = data.opportunites_par_etape.map((o: any) => o.etape);
    this.opportunitesChartData.datasets[0].data = data.opportunites_par_etape.map((o: any) => o.count);
  }

  exportCSV() { /* Implémentation export CSV */ }
  exportPDF() { /* Implémentation export PDF */ }
}

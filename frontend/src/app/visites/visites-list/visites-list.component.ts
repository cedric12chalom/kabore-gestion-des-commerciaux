import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatTableModule } from '@angular/material/table';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { MatMenuModule } from '@angular/material/menu';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { VisiteService } from '../../services/visite.service';
import { Visite } from '../../models/visite.model';

@Component({
  selector: 'app-visites-list',
  standalone: true,
  imports: [
    CommonModule, RouterModule, MatCardModule, MatTableModule, MatButtonModule,
    MatIconModule, MatChipsModule, MatMenuModule, MatProgressSpinnerModule
  ],
  template: `
    <div class="page-container">
      <div class="page-header">
        <h1>Visites</h1>
        <div class="header-actions">
          <button mat-stroked-button routerLink="/visites/calendrier">
            <mat-icon>calendar_month</mat-icon> Calendrier
          </button>
          <button mat-raised-button color="primary">
            <mat-icon>add</mat-icon> Planifier
          </button>
        </div>
      </div>

      <mat-card class="table-card">
        <div class="loading-overlay" *ngIf="isLoading">
          <mat-spinner diameter="40"></mat-spinner>
        </div>

        <table mat-table [dataSource]="visites" class="visite-table" *ngIf="!isLoading">
          <ng-container matColumnDef="date">
            <th mat-header-cell *matHeaderCellDef>Date</th>
            <td mat-cell *matCellDef="let v">{{ v.date_prevue | date:'dd/MM/yyyy HH:mm' }}</td>
          </ng-container>

          <ng-container matColumnDef="client">
            <th mat-header-cell *matHeaderCellDef>Client</th>
            <td mat-cell *matCellDef="let v">{{ v.client_nom }}</td>
          </ng-container>

          <ng-container matColumnDef="commercial">
            <th mat-header-cell *matHeaderCellDef>Commercial</th>
            <td mat-cell *matCellDef="let v">{{ v.commercial_nom }}</td>
          </ng-container>

          <ng-container matColumnDef="type">
            <th mat-header-cell *matHeaderCellDef>Type</th>
            <td mat-cell *matCellDef="let v">
              <span class="type-badge">{{ v.type_display }}</span>
            </td>
          </ng-container>

          <ng-container matColumnDef="statut">
            <th mat-header-cell *matHeaderCellDef>Statut</th>
            <td mat-cell *matCellDef="let v">
              <span class="status-badge" [class]="v.statut.toLowerCase()">
                {{ v.statut_display }}
              </span>
            </td>
          </ng-container>

          <ng-container matColumnDef="duree">
            <th mat-header-cell *matHeaderCellDef>Durée</th>
            <td mat-cell *matCellDef="let v">{{ v.duree_reelle || v.duree_estimee }} min</td>
          </ng-container>

          <ng-container matColumnDef="actions">
            <th mat-header-cell *matHeaderCellDef></th>
            <td mat-cell *matCellDef="let v">
              <button mat-icon-button [matMenuTriggerFor]="menu">
                <mat-icon>more_vert</mat-icon>
              </button>
              <mat-menu #menu="matMenu">
                <button mat-menu-item *ngIf="v.statut === 'PLANIFIEE'" (click)="checkin(v.id)">
                  <mat-icon color="primary">login</mat-icon>
                  <span>Check-in</span>
                </button>
                <button mat-menu-item *ngIf="v.statut === 'EN_COURS'" (click)="checkout(v.id)">
                  <mat-icon color="primary">logout</mat-icon>
                  <span>Check-out</span>
                </button>
              </mat-menu>
            </td>
          </ng-container>

          <tr mat-header-row *matHeaderRowDef="displayedColumns"></tr>
          <tr mat-row *matRowDef="let row; columns: displayedColumns;"></tr>
        </table>
      </mat-card>
    </div>
  `,
  styles: [`
    .page-container { padding: 0; }
    .page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
    .page-header h1 { font-size: 24px; font-weight: 600; margin: 0; }
    .header-actions { display: flex; gap: 12px; }
    .table-card { border-radius: 12px; }
    .loading-overlay { display: flex; justify-content: center; padding: 40px; }
    .visite-table { width: 100%; }
    .type-badge { padding: 4px 12px; background: var(--gray-100); border-radius: 20px; font-size: 12px; }
    .status-badge { padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 500; }
    .status-badge.planifiee { background: rgba(66, 133, 244, 0.15); color: var(--info); }
    .status-badge.en_cours { background: rgba(251, 188, 4, 0.15); color: var(--warning); }
    .status-badge.effectuee { background: rgba(52, 168, 83, 0.15); color: var(--success); }
    .status-badge.reportee { background: rgba(234, 67, 53, 0.15); color: var(--danger); }
    .status-badge.annulee { background: rgba(95, 99, 104, 0.15); color: var(--gray-600); }
  `]
})
export class VisitesListComponent implements OnInit {
  private visiteService = inject(VisiteService);

  visites: Visite[] = [];
  isLoading = true;
  displayedColumns = ['date', 'client', 'commercial', 'type', 'statut', 'duree', 'actions'];

  ngOnInit() { this.loadVisites(); }

  loadVisites() {
    this.isLoading = true;
    this.visiteService.getVisites().subscribe({
      next: (response) => {
        this.visites = response.results || response;
        this.isLoading = false;
      },
      error: () => { this.isLoading = false; }
    });
  }

  checkin(visiteId: number) {
    // Récupérer la position GPS actuelle et faire le check-in
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition((position) => {
        this.visiteService.checkin(visiteId, {
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
          precision: position.coords.accuracy,
        }).subscribe(() => this.loadVisites());
      });
    }
  }

  checkout(visiteId: number) {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition((position) => {
        this.visiteService.checkout(visiteId, {
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
          compte_rendu: '',
        }).subscribe(() => this.loadVisites());
      });
    }
  }
}

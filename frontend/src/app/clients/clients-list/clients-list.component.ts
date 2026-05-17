import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatTableModule } from '@angular/material/table';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { MatMenuModule } from '@angular/material/menu';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { FormsModule } from '@angular/forms';
import { ClientService } from '../../services/client.service';
import { Client } from '../../models/client.model';

@Component({
  selector: 'app-clients-list',
  standalone: true,
  imports: [
    CommonModule, RouterModule, MatCardModule, MatTableModule, MatInputModule,
    MatButtonModule, MatIconModule, MatChipsModule, MatMenuModule, MatProgressSpinnerModule, FormsModule
  ],
  template: `
    <div class="page-container">
      <div class="page-header">
        <h1>Clients</h1>
        <button mat-raised-button color="primary">
          <mat-icon>add</mat-icon> Nouveau client
        </button>
      </div>

      <mat-card class="table-card">
        <div class="table-filters">
          <mat-form-field appearance="outline" class="search-field">
            <mat-label>Rechercher...</mat-label>
            <input matInput [(ngModel)]="searchQuery" (keyup.enter)="applyFilter()" placeholder="Raison sociale, ville...">
            <mat-icon matPrefix>search</mat-icon>
          </mat-form-field>
        </div>

        <div class="loading-overlay" *ngIf="isLoading">
          <mat-spinner diameter="40"></mat-spinner>
        </div>

        <table mat-table [dataSource]="clients" class="client-table" *ngIf="!isLoading">
          <ng-container matColumnDef="raison_sociale">
            <th mat-header-cell *matHeaderCellDef>Client</th>
            <td mat-cell *matCellDef="let client">
              <div class="client-info">
                <span class="client-name">{{ client.raison_sociale }}</span>
                <span class="client-contact">{{ client.nom_contact }}</span>
              </div>
            </td>
          </ng-container>

          <ng-container matColumnDef="ville">
            <th mat-header-cell *matHeaderCellDef>Ville</th>
            <td mat-cell *matCellDef="let client">{{ client.ville }}</td>
          </ng-container>

          <ng-container matColumnDef="secteur">
            <th mat-header-cell *matHeaderCellDef>Secteur</th>
            <td mat-cell *matCellDef="let client">
              <span class="sector-badge">{{ client.secteur }}</span>
            </td>
          </ng-container>

          <ng-container matColumnDef="potentiel">
            <th mat-header-cell *matHeaderCellDef>Potentiel</th>
            <td mat-cell *matCellDef="let client">
              <span class="potentiel-badge" [class]="'potentiel-' + client.potentiel.toLowerCase()">
                {{ client.potentiel }}
              </span>
            </td>
          </ng-container>

          <ng-container matColumnDef="commercial">
            <th mat-header-cell *matHeaderCellDef>Commercial</th>
            <td mat-cell *matCellDef="let client">{{ client.commercial_nom || '-' }}</td>
          </ng-container>

          <ng-container matColumnDef="actions">
            <th mat-header-cell *matHeaderCellDef></th>
            <td mat-cell *matCellDef="let client">
              <button mat-icon-button [matMenuTriggerFor]="menu">
                <mat-icon>more_vert</mat-icon>
              </button>
              <mat-menu #menu="matMenu">
                <a mat-menu-item [routerLink]="['/clients', client.id]">
                  <mat-icon>visibility</mat-icon>
                  <span>Voir détails</span>
                </a>
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
    .table-card { border-radius: 12px; }
    .table-filters { padding: 16px; }
    .search-field { width: 300px; }
    .client-info { display: flex; flex-direction: column; }
    .client-name { font-weight: 600; }
    .client-contact { font-size: 12px; color: var(--gray-500); }
    .sector-badge { padding: 4px 8px; background: var(--gray-100); border-radius: 4px; font-size: 12px; }
    .potentiel-badge { padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; }
    .potentiel-badge.potentiel-a { background: rgba(52, 168, 83, 0.15); color: var(--success); }
    .potentiel-badge.potentiel-b { background: rgba(66, 133, 244, 0.15); color: var(--info); }
    .potentiel-badge.potentiel-c { background: rgba(251, 188, 4, 0.15); color: var(--warning); }
    .potentiel-badge.potentiel-d { background: rgba(234, 67, 53, 0.15); color: var(--danger); }
    .loading-overlay { display: flex; justify-content: center; padding: 40px; }
  `]
})
export class ClientsListComponent implements OnInit {
  private clientService = inject(ClientService);

  clients: Client[] = [];
  isLoading = true;
  searchQuery = '';
  displayedColumns = ['raison_sociale', 'ville', 'secteur', 'potentiel', 'commercial', 'actions'];

  ngOnInit() { this.loadClients(); }

  loadClients() {
    this.isLoading = true;
    const params: any = {};
    if (this.searchQuery) params.search = this.searchQuery;

    this.clientService.getClients(params).subscribe({
      next: (response) => {
        this.clients = response.results || response;
        this.isLoading = false;
      },
      error: () => { this.isLoading = false; }
    });
  }

  applyFilter() { this.loadClients(); }
}

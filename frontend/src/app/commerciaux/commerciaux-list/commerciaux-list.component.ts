import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatTableModule } from '@angular/material/table';
import { MatPaginatorModule } from '@angular/material/paginator';
import { MatSortModule } from '@angular/material/sort';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { MatMenuModule } from '@angular/material/menu';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { FormsModule } from '@angular/forms';
import { CommercialService } from '../../services/commercial.service';
import { Commercial } from '../../models/commercial.model';

@Component({
  selector: 'app-commerciaux-list',
  standalone: true,
  imports: [
    CommonModule, RouterModule, MatCardModule, MatTableModule, MatPaginatorModule,
    MatSortModule, MatInputModule, MatButtonModule, MatIconModule, MatChipsModule,
    MatMenuModule, MatProgressSpinnerModule, FormsModule
  ],
  template: `
    <div class="page-container">
      <div class="page-header">
        <h1>Commerciaux</h1>
        <button mat-raised-button color="primary" (click)="createCommercial()">
          <mat-icon>add</mat-icon> Nouveau commercial
        </button>
      </div>

      <mat-card class="table-card">
        <div class="table-filters">
          <mat-form-field appearance="outline" class="search-field">
            <mat-label>Rechercher...</mat-label>
            <input matInput [(ngModel)]="searchQuery" (keyup.enter)="applyFilter()" placeholder="Nom, matricule, email...">
            <mat-icon matPrefix>search</mat-icon>
          </mat-form-field>

          <div class="filter-chips">
            <mat-chip-listbox>
              <mat-chip-option *ngFor="let statut of statuts" [selected]="selectedStatut === statut.value" (click)="filterByStatut(statut.value)">
                {{ statut.label }}
              </mat-chip-option>
            </mat-chip-listbox>
          </div>
        </div>

        <div class="loading-overlay" *ngIf="isLoading">
          <mat-spinner diameter="40"></mat-spinner>
        </div>

        <table mat-table [dataSource]="commerciaux" class="commercial-table" *ngIf="!isLoading">
          <ng-container matColumnDef="matricule">
            <th mat-header-cell *matHeaderCellDef>Matricule</th>
            <td mat-cell *matCellDef="let com">{{ com.matricule }}</td>
          </ng-container>

          <ng-container matColumnDef="nom">
            <th mat-header-cell *matHeaderCellDef>Nom</th>
            <td mat-cell *matCellDef="let com">
              <div class="commercial-name">
                <span class="name">{{ com.nom_complet }}</span>
                <span class="email">{{ com.email }}</span>
              </div>
            </td>
          </ng-container>

          <ng-container matColumnDef="statut">
            <th mat-header-cell *matHeaderCellDef>Statut</th>
            <td mat-cell *matCellDef="let com">
              <span class="status-badge" [class]="com.statut.toLowerCase()">
                {{ com.statut_display }}
              </span>
            </td>
          </ng-container>

          <ng-container matColumnDef="zone">
            <th mat-header-cell *matHeaderCellDef>Zone</th>
            <td mat-cell *matCellDef="let com">{{ com.zone_nom || '-' }}</td>
          </ng-container>

          <ng-container matColumnDef="objectif">
            <th mat-header-cell *matHeaderCellDef>Objectif</th>
            <td mat-cell *matCellDef="let com">
              <div class="objectif-cell">
                <span>{{ com.taux_objectif || 0 }}%</span>
                <div class="mini-progress">
                  <div class="mini-fill" [style.width.%]="Math.min(com.taux_objectif || 0, 100)"></div>
                </div>
              </div>
            </td>
          </ng-container>

          <ng-container matColumnDef="actions">
            <th mat-header-cell *matHeaderCellDef></th>
            <td mat-cell *matCellDef="let com">
              <button mat-icon-button [matMenuTriggerFor]="menu" [attr.aria-label]="'Actions pour ' + com.nom_complet">
                <mat-icon>more_vert</mat-icon>
              </button>
              <mat-menu #menu="matMenu">
                <a mat-menu-item [routerLink]="['/commerciaux', com.id]">
                  <mat-icon>visibility</mat-icon>
                  <span>Voir détails</span>
                </a>
                <a mat-menu-item [routerLink]="['/carte']" [queryParams]="{commercial: com.id}">
                  <mat-icon>map</mat-icon>
                  <span>Voir sur la carte</span>
                </a>
                <button mat-menu-item (click)="deleteCommercial(com.id)">
                  <mat-icon color="warn">delete</mat-icon>
                  <span>Supprimer</span>
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
    .page-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 24px;
    }
    .page-header h1 { font-size: 24px; font-weight: 600; margin: 0; }
    .table-card { border-radius: 12px; overflow: hidden; }
    .table-filters {
      display: flex;
      gap: 16px;
      padding: 16px;
      align-items: center;
      flex-wrap: wrap;
    }
    .search-field { width: 300px; }
    .commercial-table { width: 100%; }
    .commercial-name { display: flex; flex-direction: column; }
    .commercial-name .name { font-weight: 600; }
    .commercial-name .email { font-size: 12px; color: var(--gray-500); }
    .status-badge {
      padding: 4px 12px;
      border-radius: 20px;
      font-size: 12px;
      font-weight: 500;
    }
    .status-badge.actif { background: rgba(52, 168, 83, 0.15); color: var(--success); }
    .status-badge.conge { background: rgba(251, 188, 4, 0.15); color: var(--warning); }
    .status-badge.suspendu { background: rgba(234, 67, 53, 0.15); color: var(--danger); }
    .objectif-cell { display: flex; flex-direction: column; gap: 4px; min-width: 100px; }
    .mini-progress { height: 4px; background: var(--gray-200); border-radius: 2px; }
    .mini-fill { height: 100%; background: var(--primary); border-radius: 2px; transition: width 0.3s; }
    .loading-overlay { display: flex; justify-content: center; padding: 40px; }
  `]
})
export class CommerciauxListComponent implements OnInit {
  private commercialService = inject(CommercialService);
  private router = inject(Router);

  commerciaux: Commercial[] = [];
  isLoading = true;
  searchQuery = '';
  selectedStatut = '';
  displayedColumns = ['matricule', 'nom', 'statut', 'zone', 'objectif', 'actions'];
  Math = Math;

  statuts = [
    { value: '', label: 'Tous' },
    { value: 'ACTIF', label: 'Actif' },
    { value: 'CONGE', label: 'Congé' },
    { value: 'SUSPENDU', label: 'Suspendu' },
  ];

  ngOnInit() {
    this.loadCommerciaux();
  }

  loadCommerciaux() {
    this.isLoading = true;
    const params: any = {};
    if (this.searchQuery) params.search = this.searchQuery;
    if (this.selectedStatut) params.statut = this.selectedStatut;

    this.commercialService.getCommerciaux(params).subscribe({
      next: (response) => {
        this.commerciaux = response.results || response;
        this.isLoading = false;
      },
      error: () => { this.isLoading = false; }
    });
  }

  applyFilter() { this.loadCommerciaux(); }
  filterByStatut(statut: string) { this.selectedStatut = statut; this.loadCommerciaux(); }
  deleteCommercial(id: number) {
    if (!confirm('Supprimer ce commercial ? Son statut passera a inactif.')) return;

    this.commercialService.deleteCommercial(id).subscribe({
      next: () => this.loadCommerciaux(),
    });
  }

  createCommercial(): void {
    this.router.navigate(['/commerciaux/create']);
  }
}

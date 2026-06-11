import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatTableModule } from '@angular/material/table';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { CommandeService } from '../../services/commande.service';
import { Commande } from '../../models/commande.model';

@Component({
  selector: 'app-commandes-list',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    MatCardModule,
    MatTableModule,
    MatButtonModule,
    MatIconModule,
    MatChipsModule,
    MatProgressSpinnerModule,
  ],
  template: `
    <div class="page-container">
      <div class="page-header">
        <h1>Commandes</h1>
        <button mat-raised-button color="primary" routerLink="/commandes/create">
          <mat-icon>add</mat-icon>
          Nouvelle commande
        </button>
      </div>

      <mat-card class="table-card">
        <div class="loading" *ngIf="isLoading">
          <mat-spinner diameter="40"></mat-spinner>
        </div>

        <table mat-table [dataSource]="commandes" *ngIf="!isLoading">
          <ng-container matColumnDef="reference">
            <th mat-header-cell *matHeaderCellDef>Reference</th>
            <td mat-cell *matCellDef="let commande">{{ commande.reference }}</td>
          </ng-container>

          <ng-container matColumnDef="client">
            <th mat-header-cell *matHeaderCellDef>Client</th>
            <td mat-cell *matCellDef="let commande">{{ commande.client_nom || '-' }}</td>
          </ng-container>

          <ng-container matColumnDef="date">
            <th mat-header-cell *matHeaderCellDef>Date</th>
            <td mat-cell *matCellDef="let commande">{{ commande.date | date:'dd/MM/yyyy' }}</td>
          </ng-container>

          <ng-container matColumnDef="montant">
            <th mat-header-cell *matHeaderCellDef>Montant</th>
            <td mat-cell *matCellDef="let commande">{{ commande.montant_total | number }} FCFA</td>
          </ng-container>

          <ng-container matColumnDef="statut">
            <th mat-header-cell *matHeaderCellDef>Statut</th>
            <td mat-cell *matCellDef="let commande">
              <mat-chip>{{ commande.statut_display || commande.statut }}</mat-chip>
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
    .table-card { padding: 0; overflow: hidden; }
    .loading { display: flex; justify-content: center; padding: 48px; }
    table { width: 100%; }
  `]
})
export class CommandesListComponent implements OnInit {
  private commandeService = inject(CommandeService);

  commandes: Commande[] = [];
  displayedColumns = ['reference', 'client', 'date', 'montant', 'statut'];
  isLoading = true;

  ngOnInit(): void {
    this.loadCommandes();
  }

  loadCommandes(): void {
    this.commandeService.getCommandes().subscribe({
      next: (response) => {
        this.commandes = response.results || response.data || response || [];
        this.isLoading = false;
      },
      error: () => {
        this.isLoading = false;
      }
    });
  }

}

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
import { Opportunite } from '../../models/commande.model';

@Component({
  selector: 'app-opportunites',
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
        <h1>Opportunites</h1>
        <button mat-raised-button color="primary">
          <mat-icon>add</mat-icon>
          Nouvelle opportunite
        </button>
      </div>

      <mat-card class="table-card">
        <div class="loading" *ngIf="isLoading">
          <mat-spinner diameter="40"></mat-spinner>
        </div>

        <table mat-table [dataSource]="opportunites" *ngIf="!isLoading">
          <ng-container matColumnDef="titre">
            <th mat-header-cell *matHeaderCellDef>Titre</th>
            <td mat-cell *matCellDef="let opportunite">{{ opportunite.titre }}</td>
          </ng-container>

          <ng-container matColumnDef="client">
            <th mat-header-cell *matHeaderCellDef>Client</th>
            <td mat-cell *matCellDef="let opportunite">{{ opportunite.client_nom || '-' }}</td>
          </ng-container>

          <ng-container matColumnDef="etape">
            <th mat-header-cell *matHeaderCellDef>Etape</th>
            <td mat-cell *matCellDef="let opportunite">
              <mat-chip>{{ opportunite.etape_display || opportunite.etape }}</mat-chip>
            </td>
          </ng-container>

          <ng-container matColumnDef="probabilite">
            <th mat-header-cell *matHeaderCellDef>Probabilite</th>
            <td mat-cell *matCellDef="let opportunite">{{ opportunite.probabilite }}%</td>
          </ng-container>

          <ng-container matColumnDef="montant">
            <th mat-header-cell *matHeaderCellDef>Montant estime</th>
            <td mat-cell *matCellDef="let opportunite">{{ opportunite.montant_estime | number }} FCFA</td>
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
export class OpportunitesComponent implements OnInit {
  private commandeService = inject(CommandeService);

  opportunites: Opportunite[] = [];
  displayedColumns = ['titre', 'client', 'etape', 'probabilite', 'montant'];
  isLoading = true;

  ngOnInit(): void {
    this.loadOpportunites();
  }

  loadOpportunites(): void {
    this.commandeService.getOpportunites().subscribe({
      next: (response) => {
        this.opportunites = response.results || response.data || response || [];
        this.isLoading = false;
      },
      error: () => {
        this.isLoading = false;
      }
    });
  }
}

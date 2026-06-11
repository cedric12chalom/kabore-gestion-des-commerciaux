import { Component, inject, OnInit, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { RouterModule, Router } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatSelectModule } from '@angular/material/select';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { VisiteService } from '../../services/visite.service';
import { CommercialService } from '../../services/commercial.service';
import { ClientService } from '../../services/client.service';

@Component({
  selector: 'app-visite-form',
  standalone: true,
  imports: [
    CommonModule, ReactiveFormsModule, RouterModule, MatCardModule,
    MatInputModule, MatButtonModule, MatIconModule, MatSelectModule,
    MatFormFieldModule, MatProgressSpinnerModule, MatDatepickerModule,
    MatNativeDateModule, MatSnackBarModule,
  ],
  template: `
    <div class="page-container">
      <div class="page-header">
        <div class="header-left">
          <button mat-icon-button routerLink="/visites">
            <mat-icon>arrow_back</mat-icon>
          </button>
          <h1>Planifier une visite</h1>
        </div>
      </div>

      <mat-card class="form-card">
        <div class="loading-overlay" *ngIf="isLoading">
          <mat-spinner diameter="40"></mat-spinner>
        </div>

        <form [formGroup]="visiteForm" (ngSubmit)="onSubmit()" *ngIf="!isLoading">
          <h3>Participants</h3>
          <div class="form-grid">
            <mat-form-field appearance="outline">
              <mat-label>Commercial *</mat-label>
              <mat-select formControlName="commercial">
                <mat-option *ngFor="let com of commerciaux" [value]="com.id">
                  {{ com.nom_complet }}
                </mat-option>
              </mat-select>
              <mat-error *ngIf="visiteForm.get('commercial')?.hasError('required')">
                Le commercial est requis
              </mat-error>
            </mat-form-field>

            <mat-form-field appearance="outline">
              <mat-label>Client *</mat-label>
              <mat-select formControlName="client">
                <mat-option *ngFor="let cl of clients" [value]="cl.id">
                  {{ cl.raison_sociale }}
                </mat-option>
              </mat-select>
              <mat-error *ngIf="visiteForm.get('client')?.hasError('required')">
                Le client est requis
              </mat-error>
            </mat-form-field>
          </div>

          <h3>Détails</h3>
          <div class="form-grid">
            <mat-form-field appearance="outline">
              <mat-label>Type de visite *</mat-label>
              <mat-select formControlName="type_visite">
                <mat-option value="PRESENTATION">Présentation</mat-option>
                <mat-option value="REGULIERE">Visite régulière</mat-option>
                <mat-option value="RECOUVREMENT">Recouvrement</mat-option>
                <mat-option value="LIVRAISON">Livraison</mat-option>
                <mat-option value="AUTRE">Autre</mat-option>
              </mat-select>
              <mat-error *ngIf="visiteForm.get('type_visite')?.hasError('required')">
                Le type de visite est requis
              </mat-error>
            </mat-form-field>

            <mat-form-field appearance="outline">
            <mat-label>Date prévue *</mat-label>
            <input matInput [matDatepicker]="picker" formControlName="date_prevue">
            <mat-datepicker-toggle matSuffix [for]="picker"></mat-datepicker-toggle>
            <mat-datepicker #picker></mat-datepicker>
              <mat-error *ngIf="visiteForm.get('date_prevue')?.hasError('required')">
                La date est requise
              </mat-error>
            </mat-form-field>

            <mat-form-field appearance="outline">
              <mat-label>Durée estimée (min) *</mat-label>
              <input matInput type="number" formControlName="duree_estimee">
              <mat-error *ngIf="visiteForm.get('duree_estimee')?.hasError('required')">
                La durée est requise
              </mat-error>
            </mat-form-field>
          </div>

          <h3>Objectif</h3>
          <div class="form-grid">
            <mat-form-field appearance="outline" class="full-width">
              <mat-label>Objectif de la visite</mat-label>
              <textarea matInput formControlName="objectif" rows="3"></textarea>
            </mat-form-field>
          </div>

          <div class="form-actions">
            <button mat-raised-button color="primary" type="submit" [disabled]="visiteForm.invalid || isSaving">
              <mat-spinner diameter="20" *ngIf="isSaving"></mat-spinner>
              <span *ngIf="!isSaving">Planifier la visite</span>
            </button>
            <button mat-button type="button" routerLink="/visites">Annuler</button>
          </div>
        </form>
      </mat-card>
    </div>
  `,
  styles: [`
    .page-container { padding: 0; }
    .page-header { display: flex; align-items: center; gap: 16px; margin-bottom: 24px; }
    .page-header h1 { margin: 0; font-size: 24px; font-weight: 600; }
    .form-card { padding: 32px; border-radius: 12px; }
    .form-card h3 { font-size: 16px; font-weight: 600; margin: 24px 0 16px; color: var(--gray-800); }
    .form-card h3:first-child { margin-top: 0; }
    .form-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 16px; }
    .full-width { width: 100%; }
    .form-actions { display: flex; gap: 12px; margin-top: 24px; justify-content: flex-end; }
    .loading-overlay { display: flex; justify-content: center; padding: 60px; }
  `]
})
export class VisiteFormComponent implements OnInit {
  private fb = inject(FormBuilder);
  private visiteService = inject(VisiteService);
  private commercialService = inject(CommercialService);
  private clientService = inject(ClientService);
  private router = inject(Router);
  private snackBar: MatSnackBar = inject(MatSnackBar);

  isLoading = false;
  isSaving = false;
  commerciaux: any[] = [];
  clients: any[] = [];

  visiteForm = this.fb.group({
    commercial: [null as number | null, Validators.required],
    client: [null as number | null, Validators.required],
    type_visite: ['', Validators.required],
    date_prevue: [new Date(), Validators.required],
    duree_estimee: [60, [Validators.required, Validators.min(1)]],
    objectif: [''],
  });

  ngOnInit(): void {
    this.loadCommerciaux();
    this.loadClients();
  }

  loadCommerciaux(): void {
    this.commercialService.getCommerciaux().subscribe({
      next: (response: any) => { this.commerciaux = response.results || response; },
      error: () => {}
    });
  }

  loadClients(): void {
    this.clientService.getClients().subscribe({
      next: (response: any) => { this.clients = response.results || response; },
      error: () => {}
    });
  }

  onSubmit(): void {
    if (this.visiteForm.invalid) return;
    this.isSaving = true;

    const dateValue = this.visiteForm.value.date_prevue;
    const dateStr = dateValue instanceof Date
      ? dateValue.toISOString()
      : dateValue;

    const data = {
      commercial: this.visiteForm.value.commercial,
      client: this.visiteForm.value.client,
      type_visite: this.visiteForm.value.type_visite,
      date_prevue: dateStr,
      duree_estimee: this.visiteForm.value.duree_estimee,
      objectif: this.visiteForm.value.objectif || '',
      statut: 'PLANIFIEE',
    };

    this.visiteService.createVisite(data).subscribe({
      next: () => {
        this.isSaving = false;
        this.snackBar.open('Visite planifiée avec succès', 'Fermer', { duration: 3000, panelClass: 'success-snackbar' });
        this.router.navigate(['/visites']);
      },
      error: () => {
        this.isSaving = false;
        this.snackBar.open('Erreur lors de la planification', 'Fermer', { duration: 3000, panelClass: 'error-snackbar' });
      }
    });
  }
}

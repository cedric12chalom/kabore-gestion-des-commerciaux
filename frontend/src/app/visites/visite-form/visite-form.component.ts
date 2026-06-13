import { Component, inject, OnInit } from '@angular/core';
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
import { HttpClient } from '@angular/common/http';
import { VisiteService } from '../../services/visite.service';
import { AuthService } from '../../services/auth.service';
import { environment } from '../../../environments/environment';

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
          <h1>Planifier un contrôle PDV</h1>
        </div>
      </div>

      <mat-card class="form-card">
        <div class="loading-overlay" *ngIf="isLoading">
          <mat-spinner diameter="40"></mat-spinner>
        </div>

        <form [formGroup]="visiteForm" (ngSubmit)="onSubmit()" *ngIf="!isLoading">
          <h3>Responsable</h3>
          <div class="form-grid">
            <mat-form-field appearance="outline" *ngIf="isAdmin">
              <mat-label>Manager *</mat-label>
              <mat-select formControlName="manager">
                <mat-option *ngFor="let mgr of managers" [value]="mgr.id">
                  {{ mgr.first_name }} {{ mgr.last_name }}
                </mat-option>
              </mat-select>
            </mat-form-field>

            <mat-form-field appearance="outline" *ngIf="!isAdmin">
              <mat-label>Manager</mat-label>
              <input matInput [value]="currentManagerName" readonly>
            </mat-form-field>
          </div>

          <h3>Point de vente</h3>
          <div class="form-grid">
            <mat-form-field appearance="outline">
              <mat-label>Nom du point de vente *</mat-label>
              <input matInput formControlName="point_vente_nom">
              <mat-error *ngIf="visiteForm.get('point_vente_nom')?.hasError('required')">
                Le point de vente est requis
              </mat-error>
            </mat-form-field>

            <mat-form-field appearance="outline">
              <mat-label>Téléphone</mat-label>
              <input matInput formControlName="contact_telephone">
            </mat-form-field>

            <mat-form-field appearance="outline">
              <mat-label>Quartier</mat-label>
              <input matInput formControlName="quartier">
            </mat-form-field>

            <mat-form-field appearance="outline" class="full-width">
              <mat-label>Adresse</mat-label>
              <textarea matInput formControlName="adresse_complete" rows="2"></textarea>
            </mat-form-field>
          </div>

          <h3>Détails</h3>
          <div class="form-grid">
            <mat-form-field appearance="outline">
              <mat-label>Type de visite *</mat-label>
              <mat-select formControlName="type_visite">
                <mat-option value="CONTROLE_PDV">Contrôle point de vente</mat-option>
                <mat-option value="PRESENTATION">Présentation</mat-option>
                <mat-option value="REGULIERE">Visite régulière</mat-option>
                <mat-option value="AUTRE">Autre</mat-option>
              </mat-select>
            </mat-form-field>

            <mat-form-field appearance="outline">
              <mat-label>Date prévue *</mat-label>
              <input matInput [matDatepicker]="picker" formControlName="date_prevue">
              <mat-datepicker-toggle matSuffix [for]="picker"></mat-datepicker-toggle>
              <mat-datepicker #picker></mat-datepicker>
            </mat-form-field>

            <mat-form-field appearance="outline">
              <mat-label>Durée estimée (min) *</mat-label>
              <input matInput type="number" formControlName="duree_estimee">
            </mat-form-field>
          </div>

          <h3>Objectif</h3>
          <div class="form-grid">
            <mat-form-field appearance="outline" class="full-width">
              <mat-label>Objectif du contrôle</mat-label>
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
  private authService = inject(AuthService);
  private http = inject(HttpClient);
  private router = inject(Router);
  private snackBar = inject(MatSnackBar);

  isLoading = false;
  isSaving = false;
  isAdmin = false;
  managers: any[] = [];
  currentManagerName = '';

  visiteForm = this.fb.group({
    manager: [null as number | null],
    point_vente_nom: ['', Validators.required],
    contact_telephone: [''],
    quartier: [''],
    adresse_complete: [''],
    type_visite: ['CONTROLE_PDV', Validators.required],
    date_prevue: [new Date(), Validators.required],
    duree_estimee: [60, [Validators.required, Validators.min(1)]],
    objectif: [''],
  });

  ngOnInit(): void {
    this.isAdmin = this.authService.isAdmin();

    if (!this.authService.isAdmin() && !this.authService.isManager()) {
      this.snackBar.open('Seuls Admin/Manager peuvent planifier des visites', 'Fermer', { duration: 3000 });
      this.router.navigate(['/visites']);
      return;
    }

    const user = this.authService.getCurrentUser();
    if (user && this.authService.isManager()) {
      this.currentManagerName = `${user.first_name} ${user.last_name}`.trim();
      this.visiteForm.patchValue({ manager: user.id });
    }

    if (this.isAdmin) {
      this.loadManagers();
    }
  }

  loadManagers(): void {
    this.isLoading = true;
    this.http.get<any>(`${environment.authUrl}/users/`, { params: { role: 'MANAGER' } }).subscribe({
      next: (response) => {
        this.managers = response.results || response || [];
        this.isLoading = false;
      },
      error: () => { this.isLoading = false; }
    });
  }

  onSubmit(): void {
    if (this.visiteForm.invalid) return;
    this.isSaving = true;

    const dateValue = this.visiteForm.value.date_prevue;
    const dateStr = dateValue instanceof Date ? dateValue.toISOString() : dateValue;

    const data = {
      manager: this.visiteForm.value.manager,
      point_vente_nom: this.visiteForm.value.point_vente_nom?.trim(),
      contact_telephone: this.visiteForm.value.contact_telephone?.trim() || '',
      quartier: this.visiteForm.value.quartier?.trim() || '',
      adresse_complete: this.visiteForm.value.adresse_complete?.trim() || '',
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

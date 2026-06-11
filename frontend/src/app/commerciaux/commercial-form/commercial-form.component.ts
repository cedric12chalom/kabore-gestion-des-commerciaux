import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { RouterModule, ActivatedRoute, Router } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatSelectModule } from '@angular/material/select';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatSnackBarModule } from '@angular/material/snack-bar';
import { CommercialService } from '../../services/commercial.service';
import { Commercial, Zone } from '../../models/commercial.model';

type StatutType = 'ACTIF' | 'CONGE' | 'SUSPENDU';

@Component({
  selector: 'app-commercial-form',
  standalone: true,
  imports: [
     CommonModule, ReactiveFormsModule, RouterModule, MatCardModule,
     MatInputModule, MatButtonModule, MatIconModule, MatSelectModule,
     MatFormFieldModule, MatProgressSpinnerModule, MatSnackBarModule,
   ],
  template: `
    <div class="page-container">
      <div class="page-header">
        <div class="header-left">
          <button mat-icon-button routerLink="/commerciaux" aria-label="Retour aux commerciaux">
            <mat-icon>arrow_back</mat-icon>
          </button>
          <h1>{{ isCreateMode ? 'Nouveau commercial' : 'Modifier le commercial' }}</h1>
        </div>
      </div>

      <mat-card class="form-card">
        <div class="loading-overlay" *ngIf="isLoading">
          <mat-spinner diameter="40"></mat-spinner>
        </div>

        <form [formGroup]="commercialForm" (ngSubmit)="onSubmit()" *ngIf="!isLoading">
          <h3>Identité</h3>
          <div class="form-grid">
            <mat-form-field appearance="outline" *ngIf="!isCreateMode" class="full-width">
              <mat-label>Nom *</mat-label>
              <input matInput formControlName="nom_complet">
              <mat-error *ngIf="commercialForm.get('nom_complet')?.hasError('required')">
                Le nom est requis
              </mat-error>
            </mat-form-field>

            <mat-form-field appearance="outline" *ngIf="isCreateMode">
              <mat-label>Prénom *</mat-label>
              <input matInput formControlName="first_name">
            </mat-form-field>

            <mat-form-field appearance="outline" *ngIf="isCreateMode">
              <mat-label>Nom *</mat-label>
              <input matInput formControlName="last_name">
            </mat-form-field>

            <mat-form-field appearance="outline">
              <mat-label>Email *</mat-label>
              <input matInput formControlName="email">
              <mat-error *ngIf="commercialForm.get('email')?.hasError('required')">
                L'email est requis
              </mat-error>
              <mat-error *ngIf="commercialForm.get('email')?.hasError('email')">
                Email invalide
              </mat-error>
            </mat-form-field>

            <mat-form-field appearance="outline" *ngIf="isCreateMode">
              <mat-label>Mot de passe temporaire *</mat-label>
              <input matInput type="password" formControlName="password">
            </mat-form-field>

            <mat-form-field appearance="outline" *ngIf="isCreateMode">
              <mat-label>Téléphone principal</mat-label>
              <input matInput formControlName="phone" placeholder="+237...">
            </mat-form-field>

            <mat-form-field appearance="outline" *ngIf="isCreateMode">
              <mat-label>Téléphone terrain</mat-label>
              <input matInput formControlName="telephone_numero" placeholder="+237...">
            </mat-form-field>

            <mat-form-field appearance="outline">
              <mat-label>Matricule</mat-label>
              <input matInput formControlName="matricule">
            </mat-form-field>

            <mat-form-field appearance="outline">
              <mat-label>Statut</mat-label>
              <mat-select formControlName="statut">
                <mat-option value="ACTIF">Actif</mat-option>
                <mat-option value="CONGE">Congé</mat-option>
                <mat-option value="SUSPENDU">Suspendu</mat-option>
              </mat-select>
            </mat-form-field>

            <mat-form-field appearance="outline">
              <mat-label>Zone</mat-label>
              <mat-select formControlName="zone">
                <mat-option [value]="null">— Non assignée —</mat-option>
                <mat-option *ngFor="let z of zones" [value]="z.id">
                  {{ z.nom }} ({{ z.ville }})
                </mat-option>
              </mat-select>
            </mat-form-field>
          </div>

          <h3>Objectifs</h3>
          <div class="form-grid">
            <mat-form-field appearance="outline">
              <mat-label>Objectif mensuel (FCFA) *</mat-label>
              <input matInput type="number" formControlName="objectif_mensuel">
              <mat-error *ngIf="commercialForm.get('objectif_mensuel')?.hasError('required')">
                L'objectif mensuel est requis
              </mat-error>
            </mat-form-field>

            <mat-form-field appearance="outline">
              <mat-label>Objectif trimestriel (FCFA) *</mat-label>
              <input matInput type="number" formControlName="objectif_trimestriel">
              <mat-error *ngIf="commercialForm.get('objectif_trimestriel')?.hasError('required')">
                L'objectif trimestriel est requis
              </mat-error>
            </mat-form-field>
          </div>

          <h3>Véhicule</h3>
          <div class="form-grid">
            <mat-form-field appearance="outline">
              <mat-label>Véhicule</mat-label>
              <input matInput formControlName="vehicule">
            </mat-form-field>

            <mat-form-field appearance="outline">
              <mat-label>Immatriculation</mat-label>
              <input matInput formControlName="immatriculation">
            </mat-form-field>
          </div>

          <div class="form-actions">
            <button mat-raised-button color="primary" type="submit" [disabled]="commercialForm.invalid || isSaving">
              <mat-spinner diameter="20" *ngIf="isSaving"></mat-spinner>
              <span *ngIf="!isSaving">Enregistrer</span>
            </button>
            <button mat-button type="button" routerLink="/commerciaux">Annuler</button>
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
export class CommercialFormComponent implements OnInit {
  private fb = inject(FormBuilder);
  private commercialService = inject(CommercialService);
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private snackBar = inject(MatSnackBar);

  isLoading = false;
  isSaving = false;
  isCreateMode = true;
  zones: Zone[] = [];

  commercialForm = this.fb.group({
    nom_complet: ['', Validators.required],
    first_name: [''],
    last_name: [''],
    email: ['', [Validators.required, Validators.email]],
    password: [''],
    phone: [''],
    telephone_numero: [''],
    matricule: [''],
    statut: ['ACTIF', Validators.required],
    zone: [null as number | null],
    objectif_mensuel: [0, [Validators.required, Validators.min(0)]],
    objectif_trimestriel: [0, [Validators.required, Validators.min(0)]],
    vehicule: [''],
    immatriculation: [''],
  });

  ngOnInit(): void {
    this.loadZones();
    const id = Number(this.route.snapshot.paramMap.get('id'));
    this.isCreateMode = !id;
    this.configureModeValidators();
    if (id) {
      this.loadCommercial(id);
    }
  }

  configureModeValidators(): void {
    if (this.isCreateMode) {
      this.commercialForm.get('nom_complet')?.clearValidators();
      this.commercialForm.get('first_name')?.setValidators([Validators.required]);
      this.commercialForm.get('last_name')?.setValidators([Validators.required]);
      this.commercialForm.get('password')?.setValidators([Validators.required, Validators.minLength(8)]);
    } else {
      this.commercialForm.get('nom_complet')?.setValidators([Validators.required]);
      this.commercialForm.get('first_name')?.clearValidators();
      this.commercialForm.get('last_name')?.clearValidators();
      this.commercialForm.get('password')?.clearValidators();
    }

    ['nom_complet', 'first_name', 'last_name', 'password'].forEach(field => {
      this.commercialForm.get(field)?.updateValueAndValidity();
    });
  }

  loadZones(): void {
    this.commercialService.getZones().subscribe({
      next: (response) => { this.zones = response.results || response; },
      error: () => {}
    });
  }

  loadCommercial(id: number): void {
    this.isLoading = true;
    this.commercialService.getCommercial(id).subscribe({
      next: (commercial: Commercial) => {
        this.commercialForm.patchValue({
          nom_complet: commercial.nom_complet,
          email: commercial.email,
          matricule: commercial.matricule,
          statut: commercial.statut as 'ACTIF' | 'CONGE' | 'SUSPENDU',
          zone: commercial.zone ?? null,
          objectif_mensuel: commercial.objectif_mensuel,
          objectif_trimestriel: commercial.objectif_trimestriel,
          vehicule: commercial.vehicule || '',
          immatriculation: commercial.immatriculation || '',
        });
        this.isLoading = false;
      },
      error: () => { this.isLoading = false; }
    });
  }

  onSubmit(): void {
    if (this.commercialForm.invalid) return;
    this.isSaving = true;

    const id = Number(this.route.snapshot.paramMap.get('id'));
    const value = this.commercialForm.getRawValue();
    const data = this.isCreateMode ? {
      first_name: value.first_name?.trim(),
      last_name: value.last_name?.trim(),
      email: value.email?.trim(),
      password: value.password,
      phone: value.phone?.trim() || '',
      matricule: value.matricule?.trim() || undefined,
      statut: value.statut,
      zone: value.zone,
      objectif_mensuel: Number(value.objectif_mensuel || 0),
      objectif_trimestriel: Number(value.objectif_trimestriel || 0),
      vehicule: value.vehicule?.trim() || '',
      immatriculation: value.immatriculation?.trim() || '',
      telephones: value.telephone_numero?.trim()
        ? [{ numero: value.telephone_numero.trim(), type: 'MOBILE', is_principal: true, is_whatsapp: true }]
        : [],
    } : {
      matricule: value.matricule?.trim() || undefined,
      statut: value.statut,
      zone: value.zone,
      objectif_mensuel: Number(value.objectif_mensuel || 0),
      objectif_trimestriel: Number(value.objectif_trimestriel || 0),
      vehicule: value.vehicule?.trim() || '',
      immatriculation: value.immatriculation?.trim() || '',
    };

    const request$ = this.isCreateMode
      ? this.commercialService.createCommercial(data)
      : this.commercialService.updateCommercial(id, data);

    request$.subscribe({
      next: (commercial) => {
        this.isSaving = false;
        this.snackBar.open('Commercial mis à jour avec succès', 'Fermer', { duration: 3000, panelClass: 'success-snackbar' });
        this.router.navigate(this.isCreateMode && commercial?.id ? ['/commerciaux', commercial.id] : ['/commerciaux']);
      },
      error: () => {
        this.isSaving = false;
        this.snackBar.open('Erreur lors de la mise à jour', 'Fermer', { duration: 3000, panelClass: 'error-snackbar' });
      }
    });
  }
}

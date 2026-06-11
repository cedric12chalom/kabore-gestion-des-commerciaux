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
import { ClientService } from '../../services/client.service';
import { CommercialService } from '../../services/commercial.service';
import { Client } from '../../models/client.model';

@Component({
  selector: 'app-client-form',
  standalone: true,
  template: `
    <div class="page-container">
      <div class="page-header">
        <div class="header-left">
          <button mat-icon-button routerLink="/clients">
            <mat-icon>arrow_back</mat-icon>
          </button>
          <h1>{{ isEditMode ? 'Modifier le client' : 'Nouveau client' }}</h1>
        </div>
      </div>

      <mat-card class="form-card">
        <div class="loading-overlay" *ngIf="isLoading">
          <mat-spinner diameter="40"></mat-spinner>
        </div>

        <form [formGroup]="clientForm" (ngSubmit)="onSubmit()" *ngIf="!isLoading">
          <h3>Informations générales</h3>
          <div class="form-grid">
            <mat-form-field appearance="outline">
              <mat-label>Raison sociale *</mat-label>
              <input matInput formControlName="raison_sociale">
              <mat-error *ngIf="clientForm.get('raison_sociale')?.hasError('required')">
                La raison sociale est requise
              </mat-error>
            </mat-form-field>

            <mat-form-field appearance="outline">
              <mat-label>Nom du contact</mat-label>
              <input matInput formControlName="nom_contact">
            </mat-form-field>

            <mat-form-field appearance="outline">
              <mat-label>Email</mat-label>
              <input matInput formControlName="email">
              <mat-error *ngIf="clientForm.get('email')?.hasError('email')">
                Email invalide
              </mat-error>
            </mat-form-field>

            <mat-form-field appearance="outline">
              <mat-label>Téléphone</mat-label>
              <input matInput formControlName="telephone">
            </mat-form-field>
          </div>

          <h3>Adresse</h3>
          <div class="form-grid">
            <mat-form-field appearance="outline" class="full-width">
              <mat-label>Adresse *</mat-label>
              <input matInput formControlName="adresse">
              <mat-error *ngIf="clientForm.get('adresse')?.hasError('required')">
                L'adresse est requise
              </mat-error>
            </mat-form-field>

            <mat-form-field appearance="outline">
              <mat-label>Ville *</mat-label>
              <input matInput formControlName="ville">
              <mat-error *ngIf="clientForm.get('ville')?.hasError('required')">
                La ville est requise
              </mat-error>
            </mat-form-field>

            <mat-form-field appearance="outline">
              <mat-label>Code postal</mat-label>
              <input matInput formControlName="code_postal">
            </mat-form-field>

            <mat-form-field appearance="outline">
              <mat-label>Pays</mat-label>
              <input matInput formControlName="pays">
            </mat-form-field>
          </div>

          <h3>Géolocalisation</h3>
          <div class="form-grid">
            <mat-form-field appearance="outline">
              <mat-label>Latitude</mat-label>
              <input matInput type="number" step="any" formControlName="latitude">
            </mat-form-field>

            <mat-form-field appearance="outline">
              <mat-label>Longitude</mat-label>
              <input matInput type="number" step="any" formControlName="longitude">
            </mat-form-field>
          </div>

          <h3>Classification</h3>
          <div class="form-grid">
            <mat-form-field appearance="outline">
              <mat-label>Secteur</mat-label>
              <input matInput formControlName="secteur">
            </mat-form-field>

            <mat-form-field appearance="outline">
              <mat-label>Potentiel</mat-label>
              <mat-select formControlName="potentiel">
                <mat-option value="A">A — Très élevé</mat-option>
                <mat-option value="B">B — Élevé</mat-option>
                <mat-option value="C">C — Moyen</mat-option>
                <mat-option value="D">D — Faible</mat-option>
              </mat-select>
            </mat-form-field>

            <mat-form-field appearance="outline">
              <mat-label>Commercial référent</mat-label>
              <mat-select formControlName="commercial_referent">
                <mat-option [value]="null">— Aucun —</mat-option>
                <mat-option *ngFor="let com of commerciaux" [value]="com.id">
                  {{ com.nom_complet }}
                </mat-option>
              </mat-select>
            </mat-form-field>
          </div>

          <div class="form-actions">
            <button mat-raised-button color="primary" type="submit" [disabled]="clientForm.invalid || isSaving">
              <mat-spinner diameter="20" *ngIf="isSaving"></mat-spinner>
              <span *ngIf="!isSaving">{{ isEditMode ? 'Enregistrer' : 'Créer le client' }}</span>
            </button>
            <button mat-button type="button" routerLink="/clients">Annuler</button>
          </div>
        </form>
      </mat-card>
    </div>
  `,
  imports: [
    CommonModule, ReactiveFormsModule, RouterModule, MatCardModule,
    MatInputModule, MatButtonModule, MatIconModule, MatSelectModule,
    MatFormFieldModule, MatProgressSpinnerModule, MatSnackBarModule,
  ],
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
export class ClientFormComponent implements OnInit {
  private fb = inject(FormBuilder);
  private clientService = inject(ClientService);
  private commercialService = inject(CommercialService);
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private snackBar = inject(MatSnackBar);

  isEditMode = false;
  isLoading = false;
  isSaving = false;
  commerciaux: any[] = [];

  clientForm = this.fb.group({
    raison_sociale: ['', Validators.required],
    nom_contact: [''],
    email: ['', [Validators.email]],
    telephone: [''],
    adresse: ['', Validators.required],
    ville: ['', Validators.required],
    code_postal: [''],
    pays: ['Cameroun'],
    latitude: [null as number | null],
    longitude: [null as number | null],
    secteur: [''],
    potentiel: ['C' as 'A' | 'B' | 'C' | 'D'],
    commercial_referent: [null as number | null],
    is_actif: [true],
    notes: [''],
  });

  ngOnInit(): void {
    this.loadCommerciaux();
    const idParam = this.route.snapshot.paramMap.get('id');
    if (idParam) {
      this.isEditMode = true;
      this.loadClient(Number(idParam));
    }
  }

  loadCommerciaux(): void {
    this.commercialService.getCommerciaux().subscribe({
      next: (response) => { this.commerciaux = response.results || response; },
      error: () => {}
    });
  }

  loadClient(id: number): void {
    this.isLoading = true;
    this.clientService.getClient(id).subscribe({
      next: (client: any) => {
        this.clientForm.patchValue({
          raison_sociale: client.raison_sociale,
          nom_contact: client.nom_contact,
          email: client.email,
          telephone: client.telephone,
          adresse: client.adresse,
          ville: client.ville,
          code_postal: client.code_postal,
          pays: client.pays || 'Cameroun',
          latitude: client.latitude ?? null,
          longitude: client.longitude ?? null,
          secteur: client.secteur,
          potentiel: client.potentiel || 'C',
          commercial_referent: client.commercial_referent ?? null,
          is_actif: client.is_actif ?? true,
          notes: client.notes || '',
        });
        this.isLoading = false;
      },
      error: () => { this.isLoading = false; }
    });
  }

  onSubmit(): void {
    if (this.clientForm.invalid) return;
    this.isSaving = true;

    const data = this.buildPayload();

    const request = this.isEditMode
      ? this.clientService.updateClient(Number(this.route.snapshot.paramMap.get('id')), data)
      : this.clientService.createClient(data);

    request.subscribe({
      next: () => {
        this.isSaving = false;
        this.snackBar.open(
          this.isEditMode ? 'Client mis à jour avec succès' : 'Client créé avec succès',
          'Fermer', { duration: 3000, panelClass: 'success-snackbar' }
        );
        this.router.navigate(['/clients']);
      },
      error: () => {
        this.isSaving = false;
        this.snackBar.open('Erreur lors de l\'enregistrement', 'Fermer', { duration: 3000, panelClass: 'error-snackbar' });
      }
    });
  }

  private buildPayload(): Record<string, unknown> {
    const value = this.clientForm.getRawValue();

    return {
      raison_sociale: value.raison_sociale?.trim(),
      nom_contact: value.nom_contact?.trim() || '',
      email: value.email?.trim() || '',
      telephone: value.telephone?.trim() || '',
      adresse: value.adresse?.trim(),
      ville: value.ville?.trim(),
      code_postal: value.code_postal?.trim() || '',
      pays: value.pays?.trim() || 'Cameroun',
      secteur: value.secteur || '',
      potentiel: value.potentiel,
      commercial_referent: value.commercial_referent,
      is_actif: value.is_actif,
      notes: value.notes?.trim() || '',
    };
  }
}

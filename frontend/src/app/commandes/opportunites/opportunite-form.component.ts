import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatSelectModule } from '@angular/material/select';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { CommercialService } from '../../services/commercial.service';
import { CommandeService } from '../../services/commande.service';

@Component({
  selector: 'app-opportunite-form',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    RouterModule,
    MatCardModule,
    MatInputModule,
    MatButtonModule,
    MatIconModule,
    MatSelectModule,
    MatFormFieldModule,
    MatProgressSpinnerModule,
    MatSnackBarModule,
  ],
  template: `
    <div class="page-container">
      <div class="page-header">
        <div class="header-left">
          <button mat-icon-button routerLink="/opportunites">
            <mat-icon>arrow_back</mat-icon>
          </button>
          <h1>Nouvelle opportunité</h1>
        </div>
      </div>

      <mat-card class="form-card">
        <div class="loading-overlay" *ngIf="isLoading">
          <mat-spinner diameter="40"></mat-spinner>
        </div>

        <form [formGroup]="opportuniteForm" (ngSubmit)="onSubmit()" *ngIf="!isLoading">
          <h3>Informations principales</h3>
          <div class="form-grid">
            <mat-form-field appearance="outline" class="full-width">
              <mat-label>Titre *</mat-label>
              <input matInput formControlName="titre">
            </mat-form-field>

            <mat-form-field appearance="outline">
              <mat-label>Point de vente / Contact *</mat-label>
              <input matInput formControlName="contact_nom">
            </mat-form-field>

            <mat-form-field appearance="outline">
              <mat-label>Téléphone</mat-label>
              <input matInput formControlName="contact_telephone">
            </mat-form-field>

            <mat-form-field appearance="outline" class="full-width">
              <mat-label>Commercial</mat-label>
              <mat-select formControlName="commercial">
                <mat-option *ngFor="let com of commerciaux" [value]="com.id">
                  {{ com.nom_complet }}
                </mat-option>
              </mat-select>
            </mat-form-field>

            <mat-form-field appearance="outline">
              <mat-label>Étape *</mat-label>
              <mat-select formControlName="etape">
                <mat-option value="PROSPECT">Prospect</mat-option>
                <mat-option value="QUALIFICATION">Qualification</mat-option>
                <mat-option value="OFFRE">Offre envoyée</mat-option>
                <mat-option value="NEGOCIATION">Négociation</mat-option>
                <mat-option value="GAGNE">Gagnée</mat-option>
                <mat-option value="PERDU">Perdue</mat-option>
                <mat-option value="REPORTE">Reportée</mat-option>
              </mat-select>
            </mat-form-field>

            <mat-form-field appearance="outline">
              <mat-label>Probabilité (%)</mat-label>
              <input matInput type="number" min="0" max="100" formControlName="probabilite">
            </mat-form-field>

            <mat-form-field appearance="outline">
              <mat-label>Montant estimé</mat-label>
              <input matInput type="number" min="0" step="any" formControlName="montant_estime">
            </mat-form-field>
          </div>

          <h3>Suivi</h3>
          <div class="form-grid">
            <mat-form-field appearance="outline">
              <mat-label>Date clôture prévue</mat-label>
              <input matInput type="date" formControlName="date_cloture_prevue">
            </mat-form-field>

            <mat-form-field appearance="outline" class="full-width">
              <mat-label>Description</mat-label>
              <textarea matInput rows="3" formControlName="description"></textarea>
            </mat-form-field>

            <mat-form-field appearance="outline" class="full-width">
              <mat-label>Notes</mat-label>
              <textarea matInput rows="3" formControlName="notes"></textarea>
            </mat-form-field>
          </div>

          <div class="form-actions">
            <button mat-raised-button color="primary" type="submit" [disabled]="opportuniteForm.invalid || isSaving">
              <mat-spinner diameter="20" *ngIf="isSaving"></mat-spinner>
              <span *ngIf="!isSaving">Créer l'opportunité</span>
            </button>
            <button mat-button type="button" routerLink="/opportunites">Annuler</button>
          </div>
        </form>
      </mat-card>
    </div>
  `,
  styles: [`
    .page-container { padding: 0; }
    .page-header { display: flex; align-items: center; gap: 16px; margin-bottom: 24px; }
    .header-left { display: flex; align-items: center; gap: 8px; }
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
export class OpportuniteFormComponent implements OnInit {
  private fb = inject(FormBuilder);
  private commercialService = inject(CommercialService);
  private commandeService = inject(CommandeService);
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private snackBar = inject(MatSnackBar);

  isLoading = true;
  isSaving = false;
  commerciaux: any[] = [];

  opportuniteForm = this.fb.group({
    titre: ['', Validators.required],
    description: [''],
    commercial: [null as number | null],
    contact_nom: ['', Validators.required],
    contact_telephone: [''],
    etape: ['PROSPECT', Validators.required],
    probabilite: [20, [Validators.required, Validators.min(0), Validators.max(100)]],
    montant_estime: [0, [Validators.required, Validators.min(0)]],
    date_cloture_prevue: [''],
    notes: [''],
  });

  ngOnInit(): void {
    this.loadData();
  }

  loadData(): void {
    this.isLoading = true;
    this.commercialService.getCommerciaux().subscribe({
      next: (response) => {
        this.commerciaux = response.results || response || [];
        if (this.commerciaux.length === 1) {
          this.opportuniteForm.patchValue({ commercial: this.commerciaux[0].id });
        }
        this.isLoading = false;
      },
      error: () => { this.isLoading = false; }
    });
  }

  onSubmit(): void {
    if (this.opportuniteForm.invalid) return;
    this.isSaving = true;

    const value = this.opportuniteForm.getRawValue();
    const payload = {
      titre: value.titre?.trim(),
      description: value.description?.trim() || '',
      commercial: value.commercial,
      contact_nom: value.contact_nom?.trim(),
      contact_telephone: value.contact_telephone?.trim() || '',
      etape: value.etape,
      probabilite: Number(value.probabilite),
      montant_estime: Number(value.montant_estime),
      date_cloture_prevue: value.date_cloture_prevue || null,
      notes: value.notes?.trim() || '',
    };

    this.commandeService.createOpportunite(payload).subscribe({
      next: () => {
        this.isSaving = false;
        this.snackBar.open('Opportunité créée avec succès', 'Fermer', { duration: 3000, panelClass: 'success-snackbar' });
        this.router.navigate(['/opportunites']);
      },
      error: () => {
        this.isSaving = false;
        this.snackBar.open('Erreur lors de la création de l\'opportunité', 'Fermer', { duration: 3000, panelClass: 'error-snackbar' });
      }
    });
  }
}

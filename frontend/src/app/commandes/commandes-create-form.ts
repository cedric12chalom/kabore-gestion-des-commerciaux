import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormArray, FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatSelectModule } from '@angular/material/select';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { MatTooltipModule } from '@angular/material/tooltip';
import { CommercialService } from '../services/commercial.service';
import { AuthService } from '../services/auth.service';
import { CommandeService } from '../services/commande.service';
import { NouveauProduitDialogComponent } from './nouveau-produit-dialog.component';
import { Produit } from '../models/commercial.model';

@Component({
  selector: 'app-commande-create-form',
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
    MatDialogModule,
    MatTooltipModule,
  ],
  template: `
    <div class="page-container">
      <div class="page-header">
        <div class="header-left">
          <button mat-icon-button routerLink="/commandes" aria-label="Retour aux commandes">
            <mat-icon>arrow_back</mat-icon>
          </button>
          <h1>Nouvelle commande</h1>
        </div>
      </div>

      <mat-card class="form-card">
        <div class="loading-overlay" *ngIf="isLoading">
          <mat-spinner diameter="40"></mat-spinner>
        </div>

        <form [formGroup]="commandeForm" (ngSubmit)="onSubmit()" *ngIf="!isLoading">
          <h3>Commande</h3>
          <div class="form-grid">
            <mat-form-field appearance="outline">
              <mat-label>Nom du contact *</mat-label>
              <input matInput formControlName="contact_nom">
            </mat-form-field>

            <mat-form-field appearance="outline">
              <mat-label>Téléphone *</mat-label>
              <input matInput formControlName="contact_telephone">
            </mat-form-field>

            <mat-form-field appearance="outline">
              <mat-label>Quartier *</mat-label>
              <input matInput formControlName="quartier">
            </mat-form-field>

            <mat-form-field appearance="outline">
              <mat-label>Commercial *</mat-label>
              <mat-select formControlName="commercial">
                <mat-option *ngFor="let commercial of commerciaux" [value]="commercial.id">
                  {{ commercial.nom_complet }} - {{ commercial.matricule }}
                </mat-option>
              </mat-select>
            </mat-form-field>

            <mat-form-field appearance="outline" class="full-width">
              <mat-label>Adresse complète *</mat-label>
              <textarea matInput rows="2" formControlName="adresse_complete"></textarea>
            </mat-form-field>

            <mat-form-field appearance="outline" class="full-width">
              <mat-label>Notes</mat-label>
              <textarea matInput rows="3" formControlName="notes"></textarea>
            </mat-form-field>
          </div>

          <div class="lines-header">
            <h3>Lignes de commande</h3>
            <button mat-stroked-button type="button" (click)="addLigne()">
              <mat-icon>add</mat-icon>
              Ajouter une ligne
            </button>
          </div>

          <div formArrayName="lignes" class="lines-list">
            <div class="line-card" *ngFor="let ligne of lignes.controls; let i = index" [formGroupName]="i">
              <div class="form-grid">
                <div class="product-select-row">
                  <mat-form-field appearance="outline" class="full-width">
                    <mat-label>Produit *</mat-label>
                    <mat-select formControlName="produit" (selectionChange)="onProduitChange(i)">
                      <mat-option *ngFor="let produit of produits" [value]="produit.id">
                        {{ produit.nom }} - {{ produit.reference }}
                      </mat-option>
                    </mat-select>
                  </mat-form-field>
                  <button
                    mat-icon-button
                    color="primary"
                    type="button"
                    (click)="ouvrirDialogNouveauProduit(i)"
                    matTooltip="Ajouter un nouveau produit"
                  >
                    <mat-icon>add_circle</mat-icon>
                  </button>
                </div>

                <mat-form-field appearance="outline">
                  <mat-label>Quantité *</mat-label>
                  <input matInput type="number" min="1" formControlName="quantite">
                </mat-form-field>

                <mat-form-field appearance="outline">
                  <mat-label>Prix unitaire *</mat-label>
                  <input matInput type="number" min="0" step="any" formControlName="prix_unitaire">
                </mat-form-field>

                <mat-form-field appearance="outline">
                  <mat-label>Remise</mat-label>
                  <input matInput type="number" min="0" step="any" formControlName="remise">
                </mat-form-field>
              </div>

              <div class="line-actions">
                <span class="line-total">
                  Total ligne: {{ getLineTotal(i) | number }} FCFA
                </span>
                <button mat-button type="button" color="warn" (click)="removeLigne(i)" [disabled]="lignes.length === 1">
                  Supprimer
                </button>
              </div>
            </div>
          </div>

          <div class="summary">
            <strong>Total estimé</strong>
            <span>{{ getMontantTotal() | number }} FCFA</span>
          </div>

          <div class="form-actions">
            <button mat-raised-button color="primary" type="submit" [disabled]="commandeForm.invalid || isSaving">
              <mat-spinner diameter="20" *ngIf="isSaving"></mat-spinner>
              <span *ngIf="!isSaving">Créer la commande</span>
            </button>
            <button mat-button type="button" routerLink="/commandes">Annuler</button>
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
    .product-select-row { display: flex; align-items: flex-end; gap: 8px; }
    .product-select-row mat-form-field { flex: 1; }
    .lines-header { display: flex; align-items: center; justify-content: space-between; gap: 16px; margin-top: 24px; }
    .lines-list { display: flex; flex-direction: column; gap: 16px; margin-top: 16px; }
    .line-card { padding: 16px; border: 1px solid var(--gray-200); border-radius: 12px; background: var(--white); }
    .line-actions, .summary, .form-actions { display: flex; justify-content: space-between; align-items: center; gap: 12px; }
    .summary { margin-top: 24px; padding: 16px; background: var(--gray-100); border-radius: 10px; }
    .form-actions { margin-top: 24px; justify-content: flex-end; }
    .loading-overlay { display: flex; justify-content: center; padding: 60px; }
  `]
})
export class CommandeCreateFormComponent implements OnInit {
  private fb = inject(FormBuilder);
  private authService = inject(AuthService);
  private commercialService = inject(CommercialService);
  private commandeService = inject(CommandeService);
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private dialog = inject(MatDialog);
  private snackBar = inject(MatSnackBar);

  isLoading = true;
  isSaving = false;
  commerciaux: any[] = [];
  produits: Produit[] = [];

  commandeForm = this.fb.group({
    commercial: [null as number | null, Validators.required],
    contact_nom: ['', Validators.required],
    contact_telephone: ['', Validators.required],
    quartier: ['', Validators.required],
    adresse_complete: ['', Validators.required],
    notes: [''],
    lignes: this.fb.array([this.createLigneGroup()]),
  });

  ngOnInit(): void {
    this.loadData();
  }

  get lignes(): FormArray {
    return this.commandeForm.get('lignes') as FormArray;
  }

  loadData(): void {
    this.isLoading = true;
    let pending = 2;
    const done = (): void => {
      pending -= 1;
      if (pending === 0) this.isLoading = false;
    };

    if (!this.authService.isAdmin() && !this.authService.isManager()) {
      this.snackBar.open('Seuls Admin/Manager peuvent créer des commandes', 'Fermer', { duration: 3000 });
      this.router.navigate(['/commandes']);
      return;
    }

    this.chargerProduits(done);

    this.commercialService.getCommerciaux().subscribe({
      next: (response) => {
        this.commerciaux = response.results || response || [];
        if (this.commerciaux.length === 1) {
          this.commandeForm.patchValue({ commercial: this.commerciaux[0].id });
        }
        done();
      },
      error: () => done()
    });
  }

  createLigneGroup() {
    return this.fb.group({
      produit: [null as number | null, Validators.required],
      quantite: [1, [Validators.required, Validators.min(1)]],
      prix_unitaire: [0, [Validators.required, Validators.min(0)]],
      remise: [0, [Validators.min(0)]],
    });
  }

  addLigne(): void {
    this.lignes.push(this.createLigneGroup());
  }

  chargerProduits(done?: () => void): void {
    this.commercialService.getProduits().subscribe({
      next: (response) => {
        this.produits = response.results || response || [];
        if (done) done();
      },
      error: () => {
        if (done) done();
      }
    });
  }

  ouvrirDialogNouveauProduit(index: number): void {
    const dialogRef = this.dialog.open(NouveauProduitDialogComponent, {
      width: '500px',
      disableClose: true,
    });

    dialogRef.afterClosed().subscribe((nouveauProduit: Produit | null) => {
      if (!nouveauProduit) {
        return;
      }

      this.chargerProduits();
      const ligne = this.lignes.at(index);
      ligne.patchValue({
        produit: nouveauProduit.id,
        prix_unitaire: nouveauProduit.prix_unitaire,
      });
    });
  }

  removeLigne(index: number): void {
    if (this.lignes.length > 1) {
      this.lignes.removeAt(index);
    }
  }

  onProduitChange(index: number): void {
    const ligne = this.lignes.at(index);
    const produitId = ligne.get('produit')?.value;
    const produit = this.produits.find(item => item.id === produitId);

    if (produit) {
      ligne.patchValue({ prix_unitaire: produit.prix_unitaire });
    }
  }

  getLineTotal(index: number): number {
    const ligne = this.lignes.at(index).value;
    const quantite = Number(ligne.quantite || 0);
    const prixUnitaire = Number(ligne.prix_unitaire || 0);
    const remise = Number(ligne.remise || 0);
    return (quantite * prixUnitaire) - remise;
  }

  getMontantTotal(): number {
    return this.lignes.controls.reduce((total, _, index) => total + this.getLineTotal(index), 0);
  }

  onSubmit(): void {
    if (this.commandeForm.invalid) return;
    this.isSaving = true;

    const value = this.commandeForm.getRawValue();
    const payload = {
      commercial: value.commercial,
      contact_nom: value.contact_nom?.trim(),
      contact_telephone: value.contact_telephone?.trim(),
      quartier: value.quartier?.trim(),
      adresse_complete: value.adresse_complete?.trim(),
      notes: value.notes?.trim() || '',
      lignes: value.lignes.map(ligne => ({
        produit: ligne.produit,
        quantite: Number(ligne.quantite),
        prix_unitaire: Number(ligne.prix_unitaire),
        remise: Number(ligne.remise || 0),
      })),
    };

    this.commandeService.createCommande(payload).subscribe({
      next: () => {
        this.isSaving = false;
        this.snackBar.open('Commande créée avec succès', 'Fermer', { duration: 3000, panelClass: 'success-snackbar' });
        this.router.navigate(['/commandes']);
      },
      error: () => {
        this.isSaving = false;
        this.snackBar.open('Erreur lors de la création de la commande', 'Fermer', { duration: 3000, panelClass: 'error-snackbar' });
      }
    });
  }
}

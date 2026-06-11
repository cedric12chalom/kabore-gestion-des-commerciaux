import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { CommercialService } from '../services/commercial.service';
import { Produit } from '../models/commercial.model';

@Component({
  selector: 'app-nouveau-produit-dialog',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatDialogModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatButtonModule,
    MatProgressSpinnerModule,
    MatSnackBarModule,
  ],
  template: `
    <h2 mat-dialog-title>Nouveau Produit</h2>

    <mat-dialog-content>
      <form [formGroup]="produitForm" class="produit-form">
        <mat-form-field appearance="outline" class="full-width">
          <mat-label>Référence *</mat-label>
          <input matInput formControlName="reference" placeholder="PRD-001">
        </mat-form-field>

        <mat-form-field appearance="outline" class="full-width">
          <mat-label>Nom *</mat-label>
          <input matInput formControlName="nom" placeholder="Smartphone Galaxy S24">
        </mat-form-field>

        <mat-form-field appearance="outline" class="full-width">
          <mat-label>Catégorie *</mat-label>
          <mat-select formControlName="categorie">
            <mat-option value="ELECTRONIQUE">Électronique</mat-option>
            <mat-option value="ALIMENTAIRE">Alimentaire</mat-option>
            <mat-option value="SANTE">Santé</mat-option>
            <mat-option value="AUTRE">Autre</mat-option>
          </mat-select>
        </mat-form-field>

        <mat-form-field appearance="outline" class="full-width">
          <mat-label>Prix Unitaire *</mat-label>
          <input matInput type="number" formControlName="prix_unitaire">
          <span matSuffix>XAF</span>
        </mat-form-field>

        <mat-form-field appearance="outline" class="full-width">
          <mat-label>Prix Gros</mat-label>
          <input matInput type="number" formControlName="prix_gros">
          <span matSuffix>XAF</span>
        </mat-form-field>

        <mat-form-field appearance="outline" class="full-width">
          <mat-label>Stock initial</mat-label>
          <input matInput type="number" formControlName="stock">
        </mat-form-field>
      </form>
    </mat-dialog-content>

    <mat-dialog-actions align="end">
      <button mat-button (click)="annuler()">Annuler</button>
      <button
        mat-raised-button
        color="primary"
        type="button"
        (click)="sauvegarder()"
        [disabled]="produitForm.invalid || isLoading"
      >
        <mat-spinner diameter="20" *ngIf="isLoading"></mat-spinner>
        <span *ngIf="!isLoading">Créer</span>
      </button>
    </mat-dialog-actions>
  `,
  styles: [
    `
      .produit-form { display: grid; gap: 16px; }
      .full-width { width: 100%; }
    `
  ]
})
export class NouveauProduitDialogComponent {
  private fb = inject(FormBuilder);
  private dialogRef = inject(MatDialogRef<NouveauProduitDialogComponent>);
  private commercialService = inject(CommercialService);
  private snackBar = inject(MatSnackBar);

  produitForm = this.fb.group({
    reference: ['', [Validators.required]],
    nom: ['', [Validators.required]],
    categorie: ['ELECTRONIQUE', [Validators.required]],
    prix_unitaire: [0, [Validators.required, Validators.min(0)]],
    prix_gros: [null],
    stock: [0, [Validators.min(0)]],
  });

  isLoading = false;

  annuler(): void {
    this.dialogRef.close(null);
  }

  sauvegarder(): void {
    if (this.produitForm.invalid) {
      this.produitForm.markAllAsTouched();
      return;
    }

    const payload = this.produitForm.value as Partial<Produit>;
    this.isLoading = true;
    this.commercialService.createProduit(payload).subscribe({
      next: (produit: Produit) => {
        this.isLoading = false;
        this.snackBar.open('Produit créé avec succès !', 'Fermer', {
          duration: 3000,
          panelClass: 'success-snackbar'
        });
        this.dialogRef.close(produit);
      },
      error: (err) => {
        this.isLoading = false;
        this.snackBar.open(
          err.error?.detail || 'Erreur lors de la création du produit',
          'Fermer',
          { duration: 5000, panelClass: 'error-snackbar' }
        );
      }
    });
  }
}

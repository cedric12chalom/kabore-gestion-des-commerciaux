import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatTabsModule } from '@angular/material/tabs';
import { MatSnackBar } from '@angular/material/snack-bar';
import { AuthService } from '../../services/auth.service';
import { User, ChangePasswordData } from '../../models/user.model';

@Component({
  selector: 'app-profil',
  standalone: true,
  imports: [
    CommonModule, ReactiveFormsModule, MatCardModule, MatInputModule,
    MatButtonModule, MatIconModule, MatTabsModule
  ],
  template: `
    <div class="profil-container">
      <h1>Mon Profil</h1>

      <mat-tab-group>
        <mat-tab label="Informations">
          <mat-card class="profil-card">
            <form [formGroup]="profilForm" (ngSubmit)="updateProfil()">
              <div class="profil-header">
                <div class="avatar-large">
                  <img *ngIf="user?.photo" [src]="user?.photo" alt="Photo">
                  <mat-icon *ngIf="!user?.photo">account_circle</mat-icon>
                </div>
                <div class="profil-info">
                  <h2>{{ user?.first_name }} {{ user?.last_name }}</h2>
                  <span class="role-badge">{{ user?.role_display }}</span>
                  <p class="email">{{ user?.email }}</p>
                </div>
              </div>

              <div class="form-grid">
                <mat-form-field appearance="outline">
                  <mat-label>Prénom</mat-label>
                  <input matInput formControlName="first_name">
                </mat-form-field>

                <mat-form-field appearance="outline">
                  <mat-label>Nom</mat-label>
                  <input matInput formControlName="last_name">
                </mat-form-field>

                <mat-form-field appearance="outline">
                  <mat-label>Téléphone</mat-label>
                  <input matInput formControlName="phone" placeholder="+237 6XX XXX XXX">
                  <mat-icon matPrefix>phone</mat-icon>
                </mat-form-field>
              </div>

              <div class="form-actions">
                <button mat-raised-button color="primary" type="submit" [disabled]="profilForm.invalid || isLoading">
                  <mat-icon>save</mat-icon> Enregistrer
                </button>
              </div>
            </form>
          </mat-card>
        </mat-tab>

        <mat-tab label="Sécurité">
          <mat-card class="profil-card">
            <form [formGroup]="passwordForm" (ngSubmit)="changePassword()">
              <h3>Changer le mot de passe</h3>

              <mat-form-field appearance="outline" class="full-width">
                <mat-label>Mot de passe actuel</mat-label>
                <input matInput type="password" formControlName="old_password">
                <mat-icon matPrefix>lock</mat-icon>
              </mat-form-field>

              <mat-form-field appearance="outline" class="full-width">
                <mat-label>Nouveau mot de passe</mat-label>
                <input matInput type="password" formControlName="new_password">
                <mat-icon matPrefix>lock_outline</mat-icon>
              </mat-form-field>

              <mat-form-field appearance="outline" class="full-width">
                <mat-label>Confirmer le mot de passe</mat-label>
                <input matInput type="password" formControlName="new_password_confirm">
                <mat-icon matPrefix>lock_outline</mat-icon>
              </mat-form-field>

              <div class="form-actions">
                <button mat-raised-button color="warn" type="submit" [disabled]="passwordForm.invalid || isLoading">
                  <mat-icon>security</mat-icon> Changer le mot de passe
                </button>
              </div>
            </form>
          </mat-card>
        </mat-tab>
      </mat-tab-group>
    </div>
  `,
  styles: [`
    .profil-container { padding: 0; }
    .profil-container h1 { font-size: 24px; font-weight: 600; margin-bottom: 24px; }
    .profil-card { padding: 24px; border-radius: 12px; margin-top: 16px; }
    .profil-header { display: flex; align-items: center; gap: 20px; margin-bottom: 24px; }
    .avatar-large { width: 80px; height: 80px; border-radius: 50%; background: var(--gray-200); display: flex; align-items: center; justify-content: center; overflow: hidden; }
    .avatar-large img { width: 100%; height: 100%; object-fit: cover; }
    .avatar-large mat-icon { font-size: 80px; width: 80px; height: 80px; color: var(--gray-500); }
    .profil-info h2 { margin: 0; font-size: 20px; }
    .role-badge { display: inline-block; padding: 4px 12px; background: var(--primary); color: white; border-radius: 20px; font-size: 12px; font-weight: 500; margin-top: 4px; }
    .email { color: var(--gray-500); margin-top: 4px; }
    .form-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 16px; margin-bottom: 24px; }
    .full-width { width: 100%; }
    .form-actions { display: flex; justify-content: flex-end; }
  `]
})
export class ProfilComponent implements OnInit {
  private fb = inject(FormBuilder);
  private authService = inject(AuthService);
  private snackBar = inject(MatSnackBar);

  user = this.authService.getCurrentUser();
  isLoading = false;

  profilForm = this.fb.group({
    first_name: [this.user?.first_name || '', Validators.required],
    last_name: [this.user?.last_name || '', Validators.required],
    phone: [this.user?.phone || ''],
  });

  passwordForm = this.fb.group({
    old_password: ['', Validators.required],
    new_password: ['', [Validators.required, Validators.minLength(8)]],
    new_password_confirm: ['', Validators.required],
  });

  ngOnInit() {}

  updateProfil() {
    if (this.profilForm.invalid) return;
    this.isLoading = true;

    this.authService.updateProfile(this.profilForm.value as Partial<User>).subscribe({
      next: () => {
        this.isLoading = false;
        this.snackBar.open('Profil mis à jour', 'Fermer', { duration: 3000, panelClass: 'success-snackbar' });
      },
      error: () => {
        this.isLoading = false;
        this.snackBar.open('Erreur lors de la mise à jour', 'Fermer', { duration: 3000, panelClass: 'error-snackbar' });
      }
    });
  }

  changePassword() {
    if (this.passwordForm.invalid) return;
    const data = this.passwordForm.value as ChangePasswordData;
    if (data.new_password !== data.new_password_confirm) {
      this.snackBar.open('Les mots de passe ne correspondent pas', 'Fermer', { duration: 3000, panelClass: 'error-snackbar' });
      return;
    }

    this.isLoading = true;
    this.authService.changePassword(data).subscribe({
      next: () => {
        this.isLoading = false;
        this.snackBar.open('Mot de passe modifié - Veuillez vous reconnecter', 'Fermer', { duration: 5000, panelClass: 'success-snackbar' });
        this.passwordForm.reset();
      },
      error: () => {
        this.isLoading = false;
      }
    });
  }
}

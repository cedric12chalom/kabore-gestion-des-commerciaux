import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, ActivatedRoute } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBar } from '@angular/material/snack-bar';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatCardModule,
    MatInputModule,
    MatButtonModule,
    MatIconModule,
    MatProgressSpinnerModule,
  ],
  template: `
    <div class="login-page">
      <div class="login-container">
        <mat-card class="login-card">
          <div class="login-header">
            <div class="logo">
              <mat-icon>my_location</mat-icon>
            </div>
            <h1>GeoCommerce Pro</h1>
            <p>Gestion commerciale avec géolocalisation GPS</p>
          </div>

          <form [formGroup]="loginForm" (ngSubmit)="onSubmit()" class="login-form">
           <mat-form-field appearance="outline" class="full-width">
  <mat-label>Nom d'utilisateur</mat-label>
  <input matInput formControlName="username" placeholder="ex: admin">
  <mat-icon matPrefix>person</mat-icon>
  <mat-error *ngIf="loginForm.get('username')?.hasError('required')">
    Le nom d'utilisateur est requis
  </mat-error>
</mat-form-field>

            <mat-form-field appearance="outline" class="full-width">
              <mat-label>Mot de passe</mat-label>
              <input matInput [type]="hidePassword ? 'password' : 'text'" formControlName="password">
              <mat-icon matPrefix>lock</mat-icon>
              <button mat-icon-button matSuffix type="button" (click)="hidePassword = !hidePassword">
                <mat-icon>{{ hidePassword ? 'visibility_off' : 'visibility' }}</mat-icon>
              </button>
              <mat-error *ngIf="loginForm.get('password')?.hasError('required')">
                Le mot de passe est requis
              </mat-error>
              <mat-error *ngIf="loginForm.get('password')?.hasError('minlength')">
                Minimum 6 caractères
              </mat-error>
            </mat-form-field>

            <div class="error-message" *ngIf="errorMessage">
              <mat-icon color="warn">error</mat-icon>
              <span>{{ errorMessage }}</span>
            </div>

            <button 
              mat-raised-button 
              color="primary" 
              type="submit" 
              class="full-width login-btn"
              [disabled]="loginForm.invalid || isLoading">
              <mat-spinner diameter="20" *ngIf="isLoading"></mat-spinner>
              <span *ngIf="!isLoading">Se connecter</span>
            </button>
                 </form>

          <div class="demo-accounts">
            <p class="demo-title">Comptes de démonstration</p>
            <div class="demo-list">
              <div class="demo-item" (click)="fillDemo('admin', 'admin123')">
                <mat-icon>admin_panel_settings</mat-icon>
                <span>Admin</span>
              </div>
              <div class="demo-item" (click)="fillDemo('manager1', 'manager123')">
                <mat-icon>supervisor_account</mat-icon>
                <span>Manager</span>
              </div>
              <div class="demo-item" (click)="fillDemo('commercial1', 'commercial123')">
                <mat-icon>person_pin</mat-icon>
                <span>Commercial</span>
              </div>
            </div>
          </div>
        </mat-card>
      </div>
    </div>
  `,
  styles: [`
    .login-page {
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      padding: 20px;
    }
    .login-container {
      width: 100%;
      max-width: 420px;
    }
    .login-card {
      padding: 40px 32px;
      border-radius: 16px;
      box-shadow: 0 20px 60px rgba(0,0,0,0.3);
    }
    .login-header {
      text-align: center;
      margin-bottom: 32px;
    }
    .logo {
      width: 64px;
      height: 64px;
      background: linear-gradient(135deg, var(--primary), var(--primary-dark));
      border-radius: 16px;
      display: flex;
      align-items: center;
      justify-content: center;
      margin: 0 auto 16px;
      color: white;
    }
    .logo mat-icon {
      font-size: 36px;
      width: 36px;
      height: 36px;
    }
    .login-header h1 {
      font-size: 24px;
      font-weight: 700;
      color: var(--gray-900);
      margin-bottom: 8px;
    }
    .login-header p {
      font-size: 14px;
      color: var(--gray-500);
    }
    .login-form {
      display: flex;
      flex-direction: column;
      gap: 16px;
    }
    .full-width {
      width: 100%;
    }
    .error-message {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 12px;
      background: rgba(234, 67, 53, 0.1);
      border-radius: 8px;
      color: var(--danger);
      font-size: 13px;
    }
    .login-btn {
      height: 48px;
      font-size: 16px;
      font-weight: 600;
    }
    .demo-accounts {
      margin-top: 24px;
      padding-top: 24px;
      border-top: 1px solid var(--gray-200);
    }
    .demo-title {
      text-align: center;
      font-size: 12px;
      color: var(--gray-500);
      text-transform: uppercase;
      letter-spacing: 1px;
      margin-bottom: 12px;
    }
    .demo-list {
      display: flex;
      gap: 8px;
      justify-content: center;
    }
    .demo-item {
      display: flex;
      align-items: center;
      gap: 6px;
      padding: 8px 12px;
      background: var(--gray-100);
      border-radius: 8px;
      cursor: pointer;
      transition: all 0.2s;
      font-size: 12px;
      color: var(--gray-700);
    }
    .demo-item:hover {
      background: var(--primary);
      color: white;
    }
    .demo-item mat-icon {
      font-size: 16px;
      width: 16px;
      height: 16px;
    }
  `]
})
export class LoginComponent {
  private fb = inject(FormBuilder);
  private authService = inject(AuthService);
  private router = inject(Router);
  private route = inject(ActivatedRoute);
  private snackBar = inject(MatSnackBar);
loginForm = this.fb.group({
  username: ['', [Validators.required]],  // ← "username" au lieu de "email"
  password: ['', [Validators.required, Validators.minLength(6)]],
  });

  hidePassword = true;
  isLoading = false;
  errorMessage = '';

  onSubmit(): void {
    if (this.loginForm.invalid) return;

    this.isLoading = true;
    this.errorMessage = '';

    const credentials = {
     username: this.loginForm.value.username!,
     password: this.loginForm.value.password!,
    };

    this.authService.login(credentials).subscribe({
      next: () => {
        this.isLoading = false;
        this.snackBar.open('Connexion réussie !', 'Fermer', {
          duration: 3000,
          panelClass: 'success-snackbar',
        });

        const returnUrl = this.route.snapshot.queryParams['returnUrl'] || '/dashboard';
        this.router.navigate([returnUrl]);
      },
      error: (error) => {
        this.isLoading = false;
        this.errorMessage = error.error?.errors?.[0]?.message || `Nom d'utilisateur ou mot de passe incorrect`;
      }
    });
  }

  fillDemo(username: string, password: string): void {
    this.loginForm.patchValue({ username, password });
  }
}

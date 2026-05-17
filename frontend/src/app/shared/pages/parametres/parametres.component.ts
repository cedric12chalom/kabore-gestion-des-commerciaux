import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';

@Component({
  selector: 'app-parametres',
  standalone: true,
  imports: [CommonModule, MatCardModule, MatIconModule],
  template: `
    <div class="parametres-container">
      <h1>Paramètres Système</h1>

      <div class="settings-grid">
        <mat-card class="setting-card">
          <mat-icon>settings_applications</mat-icon>
          <h3>Configuration GPS</h3>
          <p>Intervalle d'envoi : 30 secondes</p>
          <p>Historique conservé : 90 jours</p>
        </mat-card>

        <mat-card class="setting-card">
          <mat-icon>security</mat-icon>
          <h3>Sécurité</h3>
          <p>JWT Access Token : 30 minutes</p>
          <p>JWT Refresh Token : 7 jours</p>
          <p>Rotation tokens : Activée</p>
        </mat-card>

        <mat-card class="setting-card">
          <mat-icon>notifications_active</mat-icon>
          <h3>Notifications</h3>
          <p>Alertes zones : Activées</p>
          <p>Alertes inactivité : 30 minutes</p>
        </mat-card>

        <mat-card class="setting-card">
          <mat-icon>language</mat-icon>
          <h3>Localisation</h3>
          <p>Fuseau horaire : Africa/Douala</p>
          <p>Langue : Français</p>
          <p>Devise : FCFA</p>
        </mat-card>
      </div>
    </div>
  `,
  styles: [`
    .parametres-container { padding: 0; }
    .parametres-container h1 { font-size: 24px; font-weight: 600; margin-bottom: 24px; }
    .settings-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; }
    .setting-card { padding: 24px; text-align: center; }
    .setting-card mat-icon { font-size: 40px; width: 40px; height: 40px; color: var(--primary); margin-bottom: 12px; }
    .setting-card h3 { margin: 0 0 12px; font-size: 16px; }
    .setting-card p { margin: 4px 0; font-size: 13px; color: var(--gray-500); }
  `]
})
export class ParametresComponent {}

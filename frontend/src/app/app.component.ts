import { Component, inject, OnInit } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { CommonModule } from '@angular/common';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatBadgeModule } from '@angular/material/badge';
import { MatMenuModule } from '@angular/material/menu';
import { MatSnackBarModule } from '@angular/material/snack-bar';
import { MatProgressBarModule } from '@angular/material/progress-bar';

import { SidebarComponent } from './shared/components/sidebar/sidebar.component';
import { HeaderComponent } from './shared/components/header/header.component';
import { AuthService } from './services/auth.service';
import { NotificationService } from './services/notification.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [
    CommonModule,
    RouterOutlet,
    MatSidenavModule,
    MatToolbarModule,
    MatIconModule,
    MatButtonModule,
    MatBadgeModule,
    MatMenuModule,
    MatSnackBarModule,
    MatProgressBarModule,
    SidebarComponent,
    HeaderComponent,
  ],
    template: `
    <div class="app-container" *ngIf="authService.isAuthenticated(); else loginTemplate">
      <mat-sidenav-container class="sidenav-container">
        <mat-sidenav 
          #sidenav 
          mode="side" 
          opened 
          class="sidebar"
          [class.collapsed]="isSidebarCollapsed">
          <app-sidebar [collapsed]="isSidebarCollapsed"></app-sidebar>
        </mat-sidenav>

        <mat-sidenav-content class="main-content" [class.expanded]="isSidebarCollapsed">
          <app-header 
            [sidebarCollapsed]="isSidebarCollapsed"
            (toggleSidebar)="toggleSidebar()">
          </app-header>

          <main class="page-content">
            <mat-progress-bar 
              *ngIf="loading$ | async" 
              mode="indeterminate"
              color="primary">
            </mat-progress-bar>
            <router-outlet></router-outlet>
          </main>
        </mat-sidenav-content>
      </mat-sidenav-container>
    </div>

    <ng-template #loginTemplate>
      <router-outlet></router-outlet>
    </ng-template>
  `,  // ← ✅ BACKTICK (`) ici, pas d'apostrophe (')
  styles: [`
    .app-container {
      height: 100vh;
      overflow: hidden;
    }

    .sidenav-container {
      height: 100%;
    }

    .sidebar {
      width: var(--sidebar-width);
      background: var(--white);
      border-right: 1px solid var(--gray-200);
      transition: width 0.3s ease;

      &.collapsed {
        width: var(--sidebar-collapsed);
      }
    }

    .main-content {
      background: var(--gray-100);
      min-height: 100vh;
      transition: margin-left 0.3s ease;

      &.expanded {
        margin-left: 0;
      }
    }

    .page-content {
      padding: 24px;
      min-height: calc(100vh - var(--header-height));
      overflow-y: auto;
    }

    @media (max-width: 768px) {
      .sidebar {
        width: 0 !important;
        display: none;
      }
    }
  `]

})
export class AppComponent implements OnInit {
  authService = inject(AuthService);
  notificationService = inject(NotificationService);

  isSidebarCollapsed = false;
  loading$ = this.notificationService.loading$;

  ngOnInit() {
    // Vérifier l'authentification au chargement
    this.authService.checkAuth();

    // Démarrer le polling des notifications
    if (this.authService.isAuthenticated()) {
      this.notificationService.startPolling();
    }
  }

  toggleSidebar() {
    this.isSidebarCollapsed = !this.isSidebarCollapsed;
  }
}
  
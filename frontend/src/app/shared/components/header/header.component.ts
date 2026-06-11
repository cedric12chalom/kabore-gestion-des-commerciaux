import { Component, Input, Output, EventEmitter, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatBadgeModule } from '@angular/material/badge';
import { MatMenuModule } from '@angular/material/menu';
import { MatDividerModule } from '@angular/material/divider';
import { AuthService } from '../../../services/auth.service';
import { NotificationService } from '../../../services/notification.service';

@Component({
  selector: 'app-header',
  standalone: true,
  imports: [CommonModule, RouterModule, MatToolbarModule, MatIconModule, MatButtonModule, MatBadgeModule, MatMenuModule, MatDividerModule],
  template: `
    <mat-toolbar class="header-toolbar">
      <div class="header-left">
        <button mat-icon-button (click)="toggleSidebar.emit()" class="menu-btn" aria-label="Basculer le menu lateral">
          <mat-icon>{{ sidebarCollapsed ? 'menu_open' : 'menu' }}</mat-icon>
        </button>
        <div class="breadcrumb">
          <span class="page-title">{{ getPageTitle() }}</span>
        </div>
      </div>

      <div class="header-right">
        <button
          mat-icon-button
          [matMenuTriggerFor]="notifMenu"
          class="header-btn"
          [attr.aria-label]="'Notifications - ' + unreadCount() + ' non lues'"
          [matBadge]="unreadCount()"
          [matBadgeHidden]="unreadCount() === 0"
          matBadgeColor="warn"
          [matBadgeDescription]="unreadCount() + ' nouvelles notifications'">
          <mat-icon aria-hidden="true">
            notifications
          </mat-icon>
        </button>

        <mat-menu #notifMenu="matMenu" class="notification-menu">
          <div class="notif-header">
            <span>Notifications</span>
            <button mat-button color="primary" (click)="markAllRead()">Tout lire</button>
          </div>
          <mat-divider></mat-divider>
          <div class="notif-empty" *ngIf="unreadCount() === 0">
            <mat-icon>done_all</mat-icon>
            <span>Aucune notification</span>
          </div>
        </mat-menu>

        <button mat-icon-button [matMenuTriggerFor]="profileMenu" class="header-btn profile-btn" aria-label="Ouvrir le menu du profil">
          <div class="avatar">
            <img *ngIf="user?.photo" [src]="user?.photo" alt="">
            <mat-icon *ngIf="!user?.photo">account_circle</mat-icon>
          </div>
        </button>

        <mat-menu #profileMenu="matMenu">
          <div class="profile-header">
            <span class="profile-name">{{ user?.first_name }} {{ user?.last_name }}</span>
            <span class="profile-role">{{ user?.role_display }}</span>
          </div>
          <mat-divider></mat-divider>
          <a mat-menu-item routerLink="/profil">
            <mat-icon>person</mat-icon>
            <span>Mon profil</span>
          </a>
          <a mat-menu-item routerLink="/parametres" *ngIf="authService.isAdmin()">
            <mat-icon>settings</mat-icon>
            <span>Paramètres</span>
          </a>
          <mat-divider></mat-divider>
          <button mat-menu-item (click)="logout()">
            <mat-icon color="warn">logout</mat-icon>
            <span>Déconnexion</span>
          </button>
        </mat-menu>
      </div>
    </mat-toolbar>
  `,
  styles: [`
    .header-toolbar {
      background: var(--white);
      border-bottom: 1px solid var(--gray-200);
      height: var(--header-height);
      padding: 0 20px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      position: sticky;
      top: 0;
      z-index: 100;
    }
    .header-left {
      display: flex;
      align-items: center;
      gap: 16px;
    }
    .menu-btn {
      color: var(--gray-600);
    }
    .page-title {
      font-size: 20px;
      font-weight: 600;
      color: var(--gray-900);
    }
    .header-right {
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .header-btn {
      color: var(--gray-600);
    }
    .profile-btn .avatar {
      width: 36px;
      height: 36px;
      border-radius: 50%;
      overflow: hidden;
      display: flex;
      align-items: center;
      justify-content: center;
      background: var(--gray-200);
    }
    .profile-btn .avatar img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
    .profile-btn .avatar mat-icon {
      font-size: 36px;
      width: 36px;
      height: 36px;
      color: var(--gray-500);
    }
    .notif-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 12px 16px;
      font-weight: 600;
    }
    .notif-empty {
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 24px;
      color: var(--gray-500);
      gap: 8px;
    }
    .profile-header {
      padding: 12px 16px;
      display: flex;
      flex-direction: column;
      gap: 4px;
    }
    .profile-name {
      font-weight: 600;
      font-size: 14px;
    }
    .profile-role {
      font-size: 12px;
      color: var(--gray-500);
    }
  `]
})
export class HeaderComponent {
  @Input() sidebarCollapsed = false;
  @Output() toggleSidebar = new EventEmitter<void>();

  authService = inject(AuthService);
  notificationService = inject(NotificationService);

  user = this.authService.getCurrentUser();
  unreadCount = this.notificationService.unreadCount;

  getPageTitle(): string {
    const url = window.location.pathname;
    const titles: { [key: string]: string } = {
      '/dashboard': 'Tableau de bord',
      '/carte': 'Carte GPS',
      '/commerciaux': 'Gestion des commerciaux',
      '/clients': 'Gestion des clients',
      '/visites': 'Planification des visites',
      '/commandes': 'Gestion des commandes',
      '/opportunites': 'Opportunités commerciales',
      '/rapports': 'Rapports & Analytics',
      '/profil': 'Mon profil',
      '/parametres': 'Paramètres système',
    };
    for (const [path, title] of Object.entries(titles)) {
      if (url.startsWith(path)) return title;
    }
    return 'GeoCommerce Pro';
  }

  markAllRead(): void {
    this.notificationService.markAllAsRead().subscribe();
  }

  logout(): void {
    this.authService.logout();
  }
}

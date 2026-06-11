import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router } from '@angular/router';
import { MatListModule } from '@angular/material/list';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';
import { AuthService } from '../../../services/auth.service';

interface NavItem {
  label: string;
  icon: string;
  route: string;
  roles: string[];
  badge?: number;
}

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [CommonModule, RouterModule, MatListModule, MatIconModule, MatTooltipModule],
  template: `
    <div class="sidebar-container" [class.collapsed]="collapsed">
      <div class="logo-section">
        <div class="logo-icon">
          <mat-icon>my_location</mat-icon>
        </div>
        <span class="logo-text" *ngIf="!collapsed">GeoCommerce</span>
      </div>

      <nav class="nav-menu" aria-label="Navigation principale">
        <a 
          *ngFor="let item of navItems" 
          class="nav-item"
          [class.active]="isActive(item.route)"
          [routerLink]="item.route"
          [attr.aria-label]="item.label"
          [attr.aria-current]="isActive(item.route) ? 'page' : null"
          [matTooltip]="collapsed ? item.label : ''"
          matTooltipPosition="right">
          <mat-icon aria-hidden="true">{{ item.icon }}</mat-icon>
          <span class="nav-label" *ngIf="!collapsed">{{ item.label }}</span>
          <span class="nav-badge" *ngIf="item.badge && !collapsed">{{ item.badge }}</span>
        </a>
      </nav>

      <div class="user-section" *ngIf="!collapsed">
        <div class="user-info">
          <div class="user-avatar">
            <img *ngIf="user?.photo" [src]="user?.photo" alt="Photo">
            <mat-icon *ngIf="!user?.photo">account_circle</mat-icon>
          </div>
          <div class="user-details">
            <span class="user-name">{{ user?.first_name }} {{ user?.last_name }}</span>
            <span class="user-role">{{ user?.role_display }}</span>
          </div>
        </div>
        <button mat-icon-button class="logout-btn" (click)="logout()" aria-label="Se deconnecter">
          <mat-icon aria-hidden="true">logout</mat-icon>
        </button>
      </div>
    </div>
  `,
  styles: [`
    .sidebar-container {
      height: 100%;
      display: flex;
      flex-direction: column;
      background: var(--white);
      transition: all 0.3s ease;
    }
    .logo-section {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 20px 16px;
      border-bottom: 1px solid var(--gray-200);
    }
    .logo-icon {
      width: 40px;
      height: 40px;
      background: linear-gradient(135deg, var(--primary), var(--primary-dark));
      border-radius: 10px;
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
      flex-shrink: 0;
    }
    .logo-icon mat-icon {
      font-size: 24px;
      width: 24px;
      height: 24px;
    }
    .logo-text {
      font-size: 18px;
      font-weight: 700;
      color: var(--gray-900);
      white-space: nowrap;
    }
    .nav-menu {
      flex: 1;
      padding: 16px 12px;
      display: flex;
      flex-direction: column;
      gap: 4px;
      overflow-y: auto;
    }
    .nav-item {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 12px 16px;
      border-radius: 10px;
      text-decoration: none;
      color: var(--gray-600);
      transition: all 0.2s ease;
      cursor: pointer;
      position: relative;
    }
    .nav-item:hover {
      background: var(--gray-100);
      color: var(--primary);
    }
    .nav-item.active {
      background: rgba(26, 115, 232, 0.1);
      color: var(--primary);
      font-weight: 500;
    }
    .nav-item mat-icon {
      font-size: 22px;
      width: 22px;
      height: 22px;
      flex-shrink: 0;
    }
    .nav-label {
      font-size: 14px;
      white-space: nowrap;
      flex: 1;
    }
    .nav-badge {
      background: var(--danger);
      color: white;
      font-size: 11px;
      padding: 2px 8px;
      border-radius: 10px;
      font-weight: 600;
    }
    .collapsed .logo-section {
      justify-content: center;
      padding: 20px 8px;
    }
    .collapsed .nav-item {
      justify-content: center;
      padding: 12px;
    }
    .user-section {
      padding: 16px;
      border-top: 1px solid var(--gray-200);
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .user-info {
      display: flex;
      align-items: center;
      gap: 10px;
      flex: 1;
      min-width: 0;
    }
    .user-avatar {
      width: 36px;
      height: 36px;
      border-radius: 50%;
      background: var(--gray-200);
      display: flex;
      align-items: center;
      justify-content: center;
      overflow: hidden;
      flex-shrink: 0;
    }
    .user-avatar img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
    .user-avatar mat-icon {
      font-size: 36px;
      width: 36px;
      height: 36px;
      color: var(--gray-500);
    }
    .user-details {
      display: flex;
      flex-direction: column;
      min-width: 0;
    }
    .user-name {
      font-size: 13px;
      font-weight: 600;
      color: var(--gray-900);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .user-role {
      font-size: 11px;
      color: var(--gray-500);
    }
    .logout-btn {
      color: var(--gray-500);
      transition: color 0.2s;
    }
    .logout-btn:hover {
      color: var(--danger);
    }
  `]
})
export class SidebarComponent {
  @Input() collapsed = false;

  user = this.authService.getCurrentUser();

  navItems: NavItem[] = [
    { label: 'Dashboard', icon: 'dashboard', route: '/dashboard', roles: ['ADMIN', 'MANAGER', 'COMMERCIAL'] },
    { label: 'Carte GPS', icon: 'map', route: '/carte', roles: ['ADMIN', 'MANAGER', 'COMMERCIAL'] },
    { label: 'Commerciaux', icon: 'people', route: '/commerciaux', roles: ['ADMIN', 'MANAGER'] },
    { label: 'Visites', icon: 'event_note', route: '/visites', roles: ['ADMIN', 'MANAGER', 'COMMERCIAL'] },
    { label: 'Commandes', icon: 'shopping_cart', route: '/commandes', roles: ['ADMIN', 'MANAGER', 'COMMERCIAL'] },
    { label: 'Opportunités', icon: 'trending_up', route: '/opportunites', roles: ['ADMIN', 'MANAGER', 'COMMERCIAL'] },
    { label: 'Rapports', icon: 'assessment', route: '/rapports', roles: ['ADMIN', 'MANAGER'] },
    { label: 'Paramètres', icon: 'settings', route: '/parametres', roles: ['ADMIN'] },
  ];

  constructor(private authService: AuthService, private router: Router) {
    const role = this.user?.role;
    this.navItems = this.navItems.filter(item => item.roles.includes(role || ''));
  }

  isActive(route: string): boolean {
    return this.router.url.startsWith(route);
  }

  logout(): void {
    this.authService.logout();
  }
}

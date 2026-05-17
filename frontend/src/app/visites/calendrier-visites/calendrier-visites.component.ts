import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { VisiteService } from '../../services/visite.service';
import { CalendrierEvent } from '../../models/visite.model';

@Component({
  selector: 'app-calendrier-visites',
  standalone: true,
  imports: [CommonModule, RouterModule, MatCardModule, MatButtonModule, MatIconModule, MatTooltipModule, MatProgressSpinnerModule],
  template: `
    <div class="page-container">
      <div class="page-header">
        <button mat-icon-button routerLink="/visites">
          <mat-icon>arrow_back</mat-icon>
        </button>
        <h1>Calendrier des Visites</h1>
      </div>

      <div class="calendar-nav">
        <button mat-icon-button (click)="changeMonth(-1)">
          <mat-icon>chevron_left</mat-icon>
        </button>
        <h2>{{ currentMonthName }} {{ currentYear }}</h2>
        <button mat-icon-button (click)="changeMonth(1)">
          <mat-icon>chevron_right</mat-icon>
        </button>
      </div>

      <div class="calendar-grid">
        <div class="weekday-header" *ngFor="let day of weekDays">{{ day }}</div>

        <div 
          class="calendar-day" 
          *ngFor="let day of calendarDays"
          [class.today]="day.isToday"
          [class.has-visits]="day.visites.length > 0">
          <span class="day-number">{{ day.date }}</span>
          <div class="day-visites">
            <div 
              class="visite-dot" 
              *ngFor="let visite of day.visites"
              [class]="visite.statut.toLowerCase()"
              [matTooltip]="visite.titre">
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .page-container { padding: 0; }
    .page-header { display: flex; align-items: center; gap: 16px; margin-bottom: 24px; }
    .page-header h1 { margin: 0; font-size: 24px; }
    .calendar-nav {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 24px;
      margin-bottom: 24px;
    }
    .calendar-nav h2 { margin: 0; font-size: 20px; font-weight: 600; min-width: 200px; text-align: center; }
    .calendar-grid {
      display: grid;
      grid-template-columns: repeat(7, 1fr);
      gap: 8px;
    }
    .weekday-header {
      text-align: center;
      font-weight: 600;
      font-size: 13px;
      color: var(--gray-500);
      padding: 12px;
      text-transform: uppercase;
    }
    .calendar-day {
      aspect-ratio: 1;
      border: 1px solid var(--gray-200);
      border-radius: 8px;
      padding: 8px;
      display: flex;
      flex-direction: column;
      align-items: center;
      cursor: pointer;
      transition: all 0.2s;
      min-height: 80px;
    }
    .calendar-day:hover { background: var(--gray-100); }
    .calendar-day.today { border-color: var(--primary); background: rgba(26, 115, 232, 0.05); }
    .calendar-day.has-visits { border-color: var(--success); }
    .day-number { font-size: 14px; font-weight: 600; }
    .day-visites { display: flex; gap: 4px; margin-top: auto; flex-wrap: wrap; justify-content: center; }
    .visite-dot { width: 8px; height: 8px; border-radius: 50%; }
    .visite-dot.planifiee { background: var(--info); }
    .visite-dot.en_cours { background: var(--warning); }
    .visite-dot.effectuee { background: var(--success); }
    .visite-dot.reportee { background: var(--danger); }
  `]
})
export class CalendrierVisitesComponent implements OnInit {
  private visiteService = inject(VisiteService);

  currentDate = new Date();
  currentMonthName = '';
  currentYear = 0;
  weekDays = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim'];
  calendarDays: any[] = [];
  visites: CalendrierEvent[] = [];

  ngOnInit() {
    this.updateCalendar();
    this.loadVisites();
  }

  updateCalendar() {
    const monthNames = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 
                        'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'];
    this.currentMonthName = monthNames[this.currentDate.getMonth()];
    this.currentYear = this.currentDate.getFullYear();

    // Générer les jours du calendrier
    const year = this.currentDate.getFullYear();
    const month = this.currentDate.getMonth();
    const firstDay = new Date(year, month, 1).getDay();
    const daysInMonth = new Date(year, month + 1, 0).getDate();

    this.calendarDays = [];
    // Jours vides avant le 1er
    for (let i = 0; i < (firstDay === 0 ? 6 : firstDay - 1); i++) {
      this.calendarDays.push({ date: '', visites: [], isToday: false });
    }
    // Jours du mois
    const today = new Date();
    for (let i = 1; i <= daysInMonth; i++) {
      const isToday = today.getDate() === i && today.getMonth() === month && today.getFullYear() === year;
      this.calendarDays.push({ date: i, visites: [], isToday });
    }
  }

  loadVisites() {
    this.visiteService.getCalendrier(
      this.currentDate.getMonth() + 1,
      this.currentDate.getFullYear()
    ).subscribe({
      next: (response) => {
        if (response.success) {
          this.visites = response.visites;
          // Associer les visites aux jours
          this.calendarDays.forEach(day => {
            if (day.date) {
              day.visites = this.visites.filter(v => {
                const vDate = new Date(v.date);
                return vDate.getDate() === day.date;
              });
            }
          });
        }
      }
    });
  }

  changeMonth(delta: number) {
    this.currentDate.setMonth(this.currentDate.getMonth() + delta);
    this.updateCalendar();
    this.loadVisites();
  }
}

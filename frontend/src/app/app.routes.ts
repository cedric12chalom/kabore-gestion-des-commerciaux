import { Routes } from '@angular/router';
import { authGuard } from './guards/auth.guard';
import { roleGuard } from './guards/role.guard';

export const routes: Routes = [
  // Auth (non protégé)
  {
    path: 'login',
    loadComponent: () => import('./auth/login/login.component').then(m => m.LoginComponent),
  },

  // Dashboards
  {
    path: 'dashboard',
    loadComponent: () => import('./dashboard/dashboard.component').then(m => m.DashboardComponent),
    canActivate: [authGuard],
  },

  // Commerciaux
  {
    path: 'commerciaux',
    loadComponent: () => import('./commerciaux/commerciaux-list/commerciaux-list.component').then(m => m.CommerciauxListComponent),
    canActivate: [authGuard, () => roleGuard(['ADMIN', 'MANAGER'])],
  },
  {
    path: 'commerciaux/:id',
    loadComponent: () => import('./commerciaux/commercial-detail/commercial-detail.component').then(m => m.CommercialDetailComponent),
    canActivate: [authGuard],
  },

  // Clients
  {
    path: 'clients',
    loadComponent: () => import('./clients/clients-list/clients-list.component').then(m => m.ClientsListComponent),
    canActivate: [authGuard],
  },
  {
    path: 'clients/:id',
    loadComponent: () => import('./clients/client-detail/client-detail.component').then(m => m.ClientDetailComponent),
    canActivate: [authGuard],
  },

  // Visites
  {
    path: 'visites',
    loadComponent: () => import('./visites/visites-list/visites-list.component').then(m => m.VisitesListComponent),
    canActivate: [authGuard],
  },
  {
    path: 'visites/calendrier',
    loadComponent: () => import('./visites/calendrier-visites/calendrier-visites.component').then(m => m.CalendrierVisitesComponent),
    canActivate: [authGuard],
  },

  // GPS / Carte
  {
    path: 'carte',
    loadComponent: () => import('./gps/carte-gps/carte-gps.component').then(m => m.CarteGpsComponent),
    canActivate: [authGuard],
  },
  {
    path: 'carte/historique',
    loadComponent: () => import('./gps/historique-gps/historique-gps.component').then(m => m.HistoriqueGpsComponent),
    canActivate: [authGuard],
  },

  // Commandes
  {
    path: 'commandes',
    loadComponent: () => import('./commandes/commandes-list/commandes-list.component').then(m => m.CommandesListComponent),
    canActivate: [authGuard],
  },
  {
    path: 'opportunites',
    loadComponent: () => import('./commandes/opportunites/opportunites.component').then(m => m.OpportunitesComponent),
    canActivate: [authGuard],
  },

  // Rapports
  {
    path: 'rapports',
    loadComponent: () => import('./rapports/rapports.component').then(m => m.RapportsComponent),
    canActivate: [authGuard, () => roleGuard(['ADMIN', 'MANAGER'])],
  },

  // Profil
  {
    path: 'profil',
    loadComponent: () => import('./auth/profil/profil.component').then(m => m.ProfilComponent),
    canActivate: [authGuard],
  },

  // Paramètres
  {
    path: 'parametres',
    loadComponent: () => import('./shared/pages/parametres/parametres.component').then(m => m.ParametresComponent),
    canActivate: [authGuard, () => roleGuard(['ADMIN'])],
  },

  // Redirections
  { path: '', redirectTo: '/dashboard', pathMatch: 'full' },
  { path: '**', redirectTo: '/dashboard' },
];

import { HttpInterceptorFn, HttpErrorResponse } from '@angular/common/http';
import { inject } from '@angular/core';
import { catchError, throwError } from 'rxjs';
import { Router } from '@angular/router';
import { MatSnackBar } from '@angular/material/snack-bar';
import { AuthService } from '../services/auth.service';

export const errorInterceptor: HttpInterceptorFn = (req, next) => {
  const router = inject(Router);
  const snackBar = inject(MatSnackBar);
  const authService = inject(AuthService);

  return next(req).pipe(
    catchError((error: HttpErrorResponse) => {
      let message = 'Une erreur est survenue';

      switch (error.status) {
        case 400:
          message = error.error?.errors?.[0]?.message || 'Requête invalide';
          break;
        case 401:
          message = 'Session expirée - Veuillez vous reconnecter';
          authService.logout();
          router.navigate(['/login']);
          break;
        case 403:
          message = "Accès refusé - Vous n'avez pas les permissions";
          break;
        case 404:
          message = 'Ressource non trouvée';
          break;
        case 429:
          message = 'Trop de requêtes - Veuillez patienter';
          break;
        case 500:
          message = 'Erreur serveur - Veuillez réessayer plus tard';
          break;
      }

      if (error.status !== 401) {
        snackBar.open(message, 'Fermer', {
          duration: 5000,
          panelClass: 'error-snackbar',
        });
      }

      return throwError(() => error);
    })
  );
};

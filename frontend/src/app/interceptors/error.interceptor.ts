import { HttpInterceptorFn, HttpErrorResponse } from '@angular/common/http';
import { inject } from '@angular/core';
import { catchError, throwError } from 'rxjs';
import { Router } from '@angular/router';
import { MatSnackBar } from '@angular/material/snack-bar';
import { TokenService } from '../services/token.service';

// Ne plus injecter AuthService ici (évite la boucle HttpClient -> Interceptor -> AuthService)
export const errorInterceptor: HttpInterceptorFn = (req, next) => {
  const router = inject(Router);
  const snackBar = inject(MatSnackBar);
  const tokenService = inject(TokenService);

  return next(req).pipe(
    catchError((error: HttpErrorResponse) => {
      console.error('HTTP error', {
        method: req.method,
        url: req.urlWithParams,
        status: error.status,
        statusText: error.statusText,
        response: error.error,
      });

      let message = extractErrorMessage(error);

      switch (error.status) {
        case 400:
          message = error.error?.errors?.[0]?.message || 'Requête invalide';
          break;
        case 401:
          message = 'Session expirée - Veuillez vous reconnecter';
          // Clear tokens and redirect without calling AuthService to avoid DI loops
          tokenService.clearTokens();
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

      if (error.status === 400 || error.status >= 500) {
        message = extractErrorMessage(error);
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

function extractErrorMessage(error: HttpErrorResponse): string {
  const payload = error.error;

  if (!payload) return 'Une erreur est survenue';
  if (typeof payload === 'string') return payload;
  if (payload.detail) return String(payload.detail);

  const errors = payload.errors ?? payload;
  if (errors && typeof errors === 'object') {
    const firstKey = Object.keys(errors)[0];
    const firstValue = firstKey ? errors[firstKey] : null;
    if (Array.isArray(firstValue)) return `${firstKey}: ${firstValue.join(', ')}`;
    if (typeof firstValue === 'string') return `${firstKey}: ${firstValue}`;
  }

  return 'Une erreur est survenue';
}

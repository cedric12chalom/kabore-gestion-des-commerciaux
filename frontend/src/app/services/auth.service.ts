import { Injectable, inject, signal } from '@angular/core';
import { HttpClient, HttpBackend } from '@angular/common/http';
import { Router } from '@angular/router';
import { BehaviorSubject, Observable, throwError } from 'rxjs';
import { catchError, tap } from 'rxjs/operators';
import { jwtDecode } from 'jwt-decode';
import { environment } from '../../environments/environment';
import { User, LoginCredentials, LoginResponse, ChangePasswordData } from '../models/user.model';

interface JwtPayload {
  user_id: number;
  role: string;
  email: string;
  full_name: string;
  exp: number;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private http = inject(HttpClient);
  // HttpBackend + instance séparée de HttpClient pour bypasser les interceptors
  private httpBackend = inject(HttpBackend);
  private bypassHttp = new HttpClient(this.httpBackend);
  private router = inject(Router);

  private readonly ACCESS_TOKEN_KEY = 'geocommerce_access_token';
  private readonly REFRESH_TOKEN_KEY = 'geocommerce_refresh_token';
  private readonly USER_KEY = 'geocommerce_user';

  private currentUserSubject = new BehaviorSubject<User | null>(null);
  public currentUser$ = this.currentUserSubject.asObservable();

  // Signal pour réactivité Angular 17+
  public isAuthenticatedSignal = signal<boolean>(false);

  constructor() {
    this.loadStoredAuth();
  }

  private loadStoredAuth() {
    const token = this.getAccessToken();
    const userStr = localStorage.getItem(this.USER_KEY);

    if (token && userStr) {
      try {
        const user = JSON.parse(userStr);
        this.currentUserSubject.next(user);
        this.isAuthenticatedSignal.set(true);

        // Vérifier si le token est expiré
        if (this.isTokenExpired(token)) {
          this.refreshToken().subscribe({
            error: () => this.logout()
          });
        }
      } catch {
        this.logout();
      }
    }
  }

  login(credentials: LoginCredentials): Observable<LoginResponse> {
    return this.http.post<LoginResponse>(`${environment.authUrl}/login/`, credentials)
      .pipe(
        tap(response => {
          this.setTokens(response.access, response.refresh);
          this.setUser(response.user);
          this.currentUserSubject.next(response.user);
          this.isAuthenticatedSignal.set(true);
        }),
        catchError(error => {
          return throwError(() => error);
        })
      );
  }

  logout(): void {
    const refresh = this.getRefreshToken();
    if (refresh) {
      this.http.post(`${environment.authUrl}/logout/`, { refresh }).subscribe();
    }

    this.clearAuth();
    this.router.navigate(['/login']);
  }

  logoutAll(): void {
    this.http.post(`${environment.authUrl}/logout-all/`, {}).subscribe({
      next: () => {
        this.clearAuth();
        this.router.navigate(['/login']);
      }
    });
  }

  refreshToken(): Observable<any> {
    const refresh = this.getRefreshToken();
    if (!refresh) {
      this.logout();
      return throwError(() => new Error('No refresh token'));
    }

    // Utiliser bypassHttp pour ne pas repasser par les interceptors (évite réentrance)
    return this.bypassHttp.post(`${environment.authUrl}/refresh/`, { refresh })
      .pipe(
        tap((response: any) => {
          this.setTokens(response.access, response.refresh || refresh);
        }),
        catchError(error => {
          this.logout();
          return throwError(() => error);
        })
      );
  }

  changePassword(data: ChangePasswordData): Observable<any> {
    return this.http.post(`${environment.authUrl}/change-password/`, data);
  }

  getProfile(): Observable<User> {
    return this.http.get<User>(`${environment.authUrl}/6/`);
  }

  updateProfile(user: Partial<User>): Observable<User> {
    return this.http.put<User>(`${environment.authUrl}/profile/`, user);
  }

  checkAuth(): void {
    if (this.isAuthenticated() && this.isTokenExpired(this.getAccessToken()!)) {
      this.refreshToken().subscribe();
    }
  }

  // Getters
  isAuthenticated(): boolean {
    return !!this.getAccessToken() && !!this.currentUserSubject.value;
  }

  getAccessToken(): string | null {
    return localStorage.getItem(this.ACCESS_TOKEN_KEY);
  }

  getRefreshToken(): string | null {
    return localStorage.getItem(this.REFRESH_TOKEN_KEY);
  }

  getCurrentUser(): User | null {
    return this.currentUserSubject.value;
  }

  getUserRole(): string | null {
    const user = this.getCurrentUser();
    return user?.role || null;
  }

  isAdmin(): boolean {
    return this.getUserRole() === 'ADMIN';
  }

  isManager(): boolean {
    return this.getUserRole() === 'MANAGER';
  }

  isCommercial(): boolean {
    return this.getUserRole() === 'COMMERCIAL';
  }

  // Private helpers
  private setTokens(access: string, refresh: string): void {
    localStorage.setItem(this.ACCESS_TOKEN_KEY, access);
    localStorage.setItem(this.REFRESH_TOKEN_KEY, refresh);
  }

  private setUser(user: User): void {
    localStorage.setItem(this.USER_KEY, JSON.stringify(user));
  }

  private clearAuth(): void {
    localStorage.removeItem(this.ACCESS_TOKEN_KEY);
    localStorage.removeItem(this.REFRESH_TOKEN_KEY);
    localStorage.removeItem(this.USER_KEY);
    this.currentUserSubject.next(null);
    this.isAuthenticatedSignal.set(false);
  }

  private isTokenExpired(token: string): boolean {
    try {
      const decoded = jwtDecode<JwtPayload>(token);
      return decoded.exp * 1000 < Date.now();
    } catch {
      return true;
    }
  }
}

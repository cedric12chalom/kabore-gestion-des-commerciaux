import { Injectable, inject, signal, OnDestroy } from '@angular/core';
import { environment } from '../../environments/environment';
import { AuthService } from './auth.service';

export interface GPSPayload {
  lat: number;
  lng: number;
  accuracy: number | null;
  speed: number | null;
  heading: number | null;
  timestamp: string;
}

type ConnectionState = 'disconnected' | 'connecting' | 'connected' | 'error';

@Injectable({ providedIn: 'root' })
export class GPSTrackingService implements OnDestroy {
  private auth = inject(AuthService);

  private ws: WebSocket | null = null;
  private watchId: number | null = null;
  private sendInterval: ReturnType<typeof setInterval> | null = null;
  private wakeLock: WakeLockSentinel | null = null;
  private reconnectAttempt = 0;
  private lastPosition: GeolocationPosition | null = null;
  private destroyed = false;

  readonly connectionState = signal<ConnectionState>('disconnected');
  readonly lastSentAt = signal<Date | null>(null);
  readonly isTracking = signal(false);

  private readonly SEND_INTERVAL_MS = environment.gpsUpdateInterval ?? 30_000;
  private readonly MAX_RECONNECT_ATTEMPTS = 10;

  async startTracking(): Promise<void> {
    if (!this.auth.isCommercial() || this.isTracking()) return;
    if (!navigator.geolocation) return;

    await this.requestWakeLock();
    this.isTracking.set(true);
    this.connectWebSocket();

    this.watchId = navigator.geolocation.watchPosition(
      (pos) => { this.lastPosition = pos; },
      (err) => console.error('[GPS]', err),
      { enableHighAccuracy: true, maximumAge: 10_000, timeout: 15_000 },
    );

    this.sendInterval = setInterval(() => this.sendCurrentPosition(), this.SEND_INTERVAL_MS);
  }

  stopTracking(): void {
    this.isTracking.set(false);
    this.destroyed = true;
    if (this.watchId !== null) navigator.geolocation.clearWatch(this.watchId);
    if (this.sendInterval) clearInterval(this.sendInterval);
    this.disconnectWebSocket();
    this.releaseWakeLock();
  }

  ngOnDestroy(): void {
    this.stopTracking();
  }

  private connectWebSocket(): void {
    if (this.destroyed) return;
    const token = this.auth.getAccessToken();
    if (!token) return;

    this.connectionState.set('connecting');
    this.ws = new WebSocket(`${environment.wsUrl}/gps/track/?token=${token}`);

    this.ws.onopen = () => {
      this.connectionState.set('connected');
      this.reconnectAttempt = 0;
    };

    this.ws.onclose = () => {
      this.connectionState.set('disconnected');
      if (!this.destroyed && this.isTracking()) this.scheduleReconnect();
    };

    this.ws.onerror = () => this.connectionState.set('error');
  }

  private disconnectWebSocket(): void {
    if (this.ws) {
      this.ws.onclose = null;
      this.ws.close();
      this.ws = null;
    }
    this.connectionState.set('disconnected');
  }

  private scheduleReconnect(): void {
    if (this.reconnectAttempt >= this.MAX_RECONNECT_ATTEMPTS) return;
    const delay = Math.min(1000 * 2 ** this.reconnectAttempt, 30_000);
    this.reconnectAttempt++;
    setTimeout(() => this.connectWebSocket(), delay);
  }

  private sendCurrentPosition(): void {
    if (!this.lastPosition || !this.ws || this.ws.readyState !== WebSocket.OPEN) return;
    const payload: GPSPayload = {
      lat: this.lastPosition.coords.latitude,
      lng: this.lastPosition.coords.longitude,
      accuracy: this.lastPosition.coords.accuracy ?? null,
      speed: this.lastPosition.coords.speed != null ? this.lastPosition.coords.speed * 3.6 : null,
      heading: this.lastPosition.coords.heading ?? null,
      timestamp: new Date().toISOString(),
    };
    this.ws.send(JSON.stringify(payload));
    this.lastSentAt.set(new Date());
  }

  private async requestWakeLock(): Promise<void> {
    try {
      if ('wakeLock' in navigator) {
        this.wakeLock = await navigator.wakeLock.request('screen');
      }
    } catch { /* non bloquant */ }
  }

  private async releaseWakeLock(): Promise<void> {
    if (this.wakeLock) {
      await this.wakeLock.release();
      this.wakeLock = null;
    }
  }
}

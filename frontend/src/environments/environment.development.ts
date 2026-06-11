export const environment = {
  production: false,  // ← false en dev
  apiUrl: 'http://127.0.0.1:8000/api/v1',      // ← localhost
  authUrl: 'http://127.0.0.1:8000/api/v1/auth', // ← localhost + /v1
  wsUrl: 'ws://127.0.0.1:8000/ws',              // ← localhost
  appName: 'GeoCommerce Pro',
  version: '1.0.0',
  gpsUpdateInterval: 30000,
};
export const environment = {
  production: true,
  apiUrl: (globalThis as any).__env?.apiUrl ?? 'https://kabore-gestion-des-commerciaux-3.onrender.com/api/v1',
  authUrl: (globalThis as any).__env?.authUrl ?? 'https://kabore-gestion-des-commerciaux-3.onrender.com/api/v1/auth',
  wsUrl: (globalThis as any).__env?.wsUrl ?? 'wss://kabore-gestion-des-commerciaux-3.onrender.com/ws/gps/',
  appName: 'GeoCommerce Pro',
  version: '1.0.0',
  gpsUpdateInterval: 30000,
};
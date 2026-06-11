"""
GeoCommerce Pro - ASGI Configuration
Support WebSocket pour géolocalisation temps réel
"""
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geocommerce_backend.settings')

django_asgi_app = get_asgi_application()

from apps.gps.routing import websocket_urlpatterns as gps_websocket_patterns
from apps.gps.middleware import JWTAuthMiddleware
from apps.notifications.routing import websocket_urlpatterns as notif_websocket_patterns

application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': JWTAuthMiddleware(
        URLRouter(gps_websocket_patterns + notif_websocket_patterns)
    ),
})

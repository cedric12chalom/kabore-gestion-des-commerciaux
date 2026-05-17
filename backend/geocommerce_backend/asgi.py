"""
GeoCommerce Pro - ASGI Configuration
Support WebSocket pour geolocalisation temps reel
"""
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geocommerce_backend.settings')

# Importer les routes WebSocket apres le setup Django
django_asgi_app = get_asgi_application()

from apps.gps.routing import websocket_urlpatterns as gps_websocket_patterns
from apps.notifications.routing import websocket_urlpatterns as notif_websocket_patterns

application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': AuthMiddlewareStack(
        URLRouter(
            gps_websocket_patterns + notif_websocket_patterns
        )
    ),
})

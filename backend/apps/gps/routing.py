"""
Routing WebSocket pour GPS temps réel
"""
from django.urls import re_path
from .consumers import GPSConsumer

websocket_urlpatterns = [
    re_path(r'ws/gps/(?P<commercial_id>\d+)/$', GPSConsumer.as_asgi()),
]

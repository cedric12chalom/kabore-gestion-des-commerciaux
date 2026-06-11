from django.urls import re_path
from .consumers import GPSConsumer

websocket_urlpatterns = [
    re_path(r'ws/gps/(?P<mode>track|watch)/$', GPSConsumer.as_asgi()),
]

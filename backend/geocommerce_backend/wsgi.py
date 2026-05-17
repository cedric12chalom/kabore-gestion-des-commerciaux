"""
GeoCommerce Pro - WSGI Configuration
"""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geocommerce_backend.settings')

application = get_wsgi_application()

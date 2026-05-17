"""
Middleware personnalisé pour logging et sécurité
"""
import logging
import time
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger('apps')


class RequestLoggingMiddleware(MiddlewareMixin):
    """Log toutes les requêtes API avec timing"""

    def process_request(self, request):
        request.start_time = time.time()
        return None

    def process_response(self, request, response):
        duration = time.time() - getattr(request, 'start_time', time.time())

        # Log seulement les requêtes API
        if request.path.startswith('/api/'):
            logger.info(
                f"{request.method} {request.path} - {response.status_code} - "
                f"{duration:.3f}s - User: {request.user if request.user.is_authenticated else 'Anonymous'}"
            )

        # Headers de sécurité
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'

        return response

"""
GeoCommerce Pro - Middleware personnalise
Audit logs et timing des requetes
"""
import time
import logging
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger('apps.core')


class AuditLogMiddleware(MiddlewareMixin):
    """
    Middleware d'audit : log toutes les requetes API avec utilisateur, methode, URL, statut.
    Permet de tracer qui fait quoi dans le systeme.
    """

    def process_request(self, request):
        request.start_time = time.time()
        return None

    def process_response(self, request, response):
        duration = getattr(request, 'start_time', None)
        if duration:
            duration = time.time() - duration

        user = request.user if hasattr(request, 'user') and request.user.is_authenticated else 'Anonymous'

        logger.info(
            f"AUDIT | User: {user} | Method: {request.method} | "
            f"Path: {request.path} | Status: {response.status_code} | "
            f"Duration: {duration:.3f}s | IP: {self.get_client_ip(request)}"
        )
        return response

    @staticmethod
    def get_client_ip(request):
        """Recupere l'IP reelle du client (derriere proxy/load balancer)."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', 'unknown')
        return ip


class RequestTimingMiddleware(MiddlewareMixin):
    """
    Middleware de timing : ajoute un header X-Request-Duration a chaque reponse.
    Utile pour le monitoring des performances API.
    """

    def process_request(self, request):
        request._start_time = time.time()
        return None

    def process_response(self, request, response):
        start_time = getattr(request, '_start_time', None)
        if start_time:
            duration = time.time() - start_time
            response['X-Request-Duration'] = f"{duration:.3f}s"
        return response

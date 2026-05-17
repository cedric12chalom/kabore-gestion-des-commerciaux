"""
Gestionnaire d'exceptions personnalisé
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    """Handler global pour formater toutes les erreurs API"""
    response = exception_handler(exc, context)

    if response is not None:
        # Formater les erreurs de validation DRF
        if isinstance(response.data, dict):
            errors = []
            for field, messages in response.data.items():
                if isinstance(messages, list):
                    for msg in messages:
                        errors.append({'field': field, 'message': str(msg)})
                else:
                    errors.append({'field': field, 'message': str(messages)})
            response.data = {
                'success': False,
                'errors': errors,
                'status_code': response.status_code,
            }
        else:
            response.data = {
                'success': False,
                'errors': [{'field': 'non_field_errors', 'message': str(response.data)}],
                'status_code': response.status_code,
            }
    else:
        # Erreur 500 non gérée
        response = Response({
            'success': False,
            'errors': [{'field': 'server', 'message': 'Erreur interne du serveur'}],
            'status_code': status.HTTP_500_INTERNAL_SERVER_ERROR,
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return response

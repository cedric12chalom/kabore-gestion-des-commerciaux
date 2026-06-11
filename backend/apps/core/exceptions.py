from rest_framework.views import exception_handler


def global_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        return response

    data = response.data
    detail = "Une erreur est survenue."
    errors = {}

    if isinstance(data, dict):
        if "detail" in data and len(data) == 1:
            detail = str(data["detail"])
        else:
            detail = "Veuillez corriger les erreurs indiquees."
            errors = data
    elif isinstance(data, list):
        detail = "Veuillez corriger les erreurs indiquees."
        errors = {"non_field_errors": data}
    else:
        detail = str(data)

    response.data = {
        "detail": detail,
        "errors": errors,
    }
    return response

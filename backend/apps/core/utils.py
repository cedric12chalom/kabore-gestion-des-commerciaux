"""
GeoCommerce Pro - Utilitaires
Fonctions reutilisables pour tout le backend
"""
import re
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional, Dict, Any

import phonenumbers
from phonenumbers import geocoder, carrier


def validate_phone_number(phone_number: str, region: str = "CM") -> Dict[str, Any]:
    """
    Valide un numero de telephone avec la librairie phonenumbers.

    Args:
        phone_number: Le numero a valider (ex: "+237699123456" ou "699123456")
        region: Code pays par defaut (CM = Cameroun)

    Returns:
        Dict avec is_valid, formatted, carrier_name, location

    Exemple:
        >>> validate_phone_number("+237699123456")
        {'is_valid': True, 'formatted': '+237 6 99 12 34 56', 'carrier': 'MTN', ...}
    """
    result = {
        'is_valid': False,
        'formatted': None,
        'carrier_name': None,
        'location': None,
        'e164': None,
        'error': None
    }

    try:
        # Parser le numero
        parsed = phonenumbers.parse(phone_number, region)

        # Verifier la validite
        if not phonenumbers.is_valid_number(parsed):
            result['error'] = "Numero de telephone invalide"
            return result

        result['is_valid'] = True
        result['e164'] = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
        result['formatted'] = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL)

        # Operateur telephonique
        try:
            result['carrier_name'] = carrier.name_for_number(parsed, "fr")
        except:
            result['carrier_name'] = "Inconnu"

        # Localisation
        try:
            result['location'] = geocoder.description_for_number(parsed, "fr")
        except:
            result['location'] = region

    except phonenumbers.NumberParseException as e:
        result['error'] = f"Format invalide: {str(e)}"
    except Exception as e:
        result['error'] = f"Erreur: {str(e)}"

    return result


def generate_unique_code(prefix: str = "GEO") -> str:
    """
    Genere un code unique pour les commandes, opportunites, etc.
    Format: PREFIX-YYYYMMDD-XXXX (ex: CMD-20260516-A7B2)
    """
    date_str = datetime.now().strftime("%Y%m%d")
    random_part = uuid.uuid4().hex[:4].upper()
    return f"{prefix}-{date_str}-{random_part}"


def calculate_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calcule la distance en kilometres entre deux points GPS (formule Haversine).

    Args:
        lat1, lon1: Coordonnees du point A
        lat2, lon2: Coordonnees du point B

    Returns:
        Distance en kilometres (arrondie a 2 decimales)
    """
    from math import radians, cos, sin, asin, sqrt

    # Convertir en radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    # Formule Haversine
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))

    # Rayon de la Terre en km
    r = 6371

    return round(c * r, 2)


def format_duration_minutes(minutes: int) -> str:
    """
    Formate une duree en minutes en format lisible.
    Ex: 125 -> "2h 05min"
    """
    hours = minutes // 60
    mins = minutes % 60
    if hours > 0:
        return f"{hours}h {mins:02d}min"
    return f"{mins}min"


def get_date_range(period: str) -> tuple:
    """
    Retourne le debut et la fin d'une periode donnee.

    Args:
        period: 'today', 'week', 'month', 'quarter', 'year'

    Returns:
        Tuple (date_debut, date_fin)
    """
    today = datetime.now().date()

    if period == 'today':
        return today, today
    elif period == 'week':
        start = today - timedelta(days=today.weekday())
        return start, today
    elif period == 'month':
        start = today.replace(day=1)
        return start, today
    elif period == 'quarter':
        quarter = (today.month - 1) // 3
        start = today.replace(month=quarter * 3 + 1, day=1)
        return start, today
    elif period == 'year':
        start = today.replace(month=1, day=1)
        return start, today
    else:
        return today - timedelta(days=30), today


def sanitize_filename(filename: str) -> str:
    """
    Nettoie un nom de fichier pour eviter les injections.
    """
    # Garder uniquement les caracteres alphanumeriques, points, tirets et underscores
    cleaned = re.sub(r'[^\w\-\.]', '_', filename)
    # Limiter la longueur
    return cleaned[:100]

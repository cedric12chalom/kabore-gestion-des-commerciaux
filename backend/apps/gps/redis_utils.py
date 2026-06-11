"""
Validation Redis pour le rate limiting GPS.
Fallback mémoire si Redis indisponible (dev local).
"""
import json
import time
from math import radians, sin, cos, sqrt, atan2
from django.conf import settings

RATE_LIMIT_SECONDS = 25
MIN_DISTANCE_METERS = 10
REDIS_TTL_SECONDS = 60

_memory_store: dict = {}


def _get_redis():
    try:
        import redis
        url = getattr(settings, 'CHANNEL_LAYERS_REDIS_URL', 'redis://localhost:6379/0')
        return redis.from_url(url, decode_responses=True)
    except Exception:
        return None


def haversine_m(lat1, lng1, lat2, lng2) -> float:
    R = 6_371_000
    dlat = radians(lat2 - lat1)
    dlng = radians(lng2 - lng1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlng / 2) ** 2
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))


def validate_position(commercial_id: int, payload: dict) -> tuple[bool, str]:
    """Rate limit 25s + distance min 10m."""
    now = time.time()
    r = _get_redis()

    if r:
        key_last = f"gps:last_update:{commercial_id}"
        key_pos = f"gps:last_pos:{commercial_id}"
        last_ts = r.get(key_last)
        if last_ts and (now - float(last_ts)) < RATE_LIMIT_SECONDS:
            return False, 'rate_limit'
        last_pos_raw = r.get(key_pos)
        if last_pos_raw:
            last_pos = json.loads(last_pos_raw)
            if haversine_m(last_pos['lat'], last_pos['lng'], payload['lat'], payload['lng']) < MIN_DISTANCE_METERS:
                return False, 'distance_min'
        r.set(key_last, now, ex=REDIS_TTL_SECONDS)
        r.set(key_pos, json.dumps({'lat': payload['lat'], 'lng': payload['lng']}), ex=REDIS_TTL_SECONDS)
        r.set(f"gps:current:{commercial_id}", json.dumps(payload), ex=REDIS_TTL_SECONDS)
        return True, ''

    # Fallback mémoire
    store = _memory_store.setdefault(commercial_id, {})
    if store.get('last_ts') and (now - store['last_ts']) < RATE_LIMIT_SECONDS:
        return False, 'rate_limit'
    if store.get('last_pos'):
        lp = store['last_pos']
        if haversine_m(lp['lat'], lp['lng'], payload['lat'], payload['lng']) < MIN_DISTANCE_METERS:
            return False, 'distance_min'
    store['last_ts'] = now
    store['last_pos'] = {'lat': payload['lat'], 'lng': payload['lng']}
    return True, ''

from math import asin, cos, radians, sin, sqrt

from django.conf import settings
from django.db import models

if settings.USE_GIS:
    from django.contrib.gis.db import models as gis_models
    from django.contrib.gis.geos import Point
else:
    class _LocalGisModels:
        @staticmethod
        def PointField(*args, **kwargs):
            kwargs.pop('srid', None)
            kwargs.pop('geography', None)
            return models.TextField(*args, **kwargs)

        @staticmethod
        def PolygonField(*args, **kwargs):
            kwargs.pop('srid', None)
            kwargs.pop('geography', None)
            return models.TextField(*args, **kwargs)

        @staticmethod
        def LineStringField(*args, **kwargs):
            kwargs.pop('srid', None)
            kwargs.pop('geography', None)
            return models.TextField(*args, **kwargs)

    class Point:
        def __init__(self, x, y, *args, **kwargs):
            self.x = x
            self.y = y

        def __str__(self):
            return f"POINT({self.x} {self.y})"

    gis_models = _LocalGisModels()


def point_coords(point):
    """Return (lng, lat) for GEOS Point, local Point, or WKT POINT text."""
    if not point:
        return None
    if hasattr(point, "x") and hasattr(point, "y"):
        return float(point.x), float(point.y)
    if isinstance(point, str) and point.startswith("POINT(") and point.endswith(")"):
        raw = point[6:-1].strip()
        lng, lat = raw.split()[:2]
        return float(lng), float(lat)
    return None


def distance_m(point_a, point_b):
    coords_a = point_coords(point_a)
    coords_b = point_coords(point_b)
    if not coords_a or not coords_b:
        return None

    lng1, lat1 = coords_a
    lng2, lat2 = coords_b
    radius_m = 6_371_000
    dlat = radians(lat2 - lat1)
    dlng = radians(lng2 - lng1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlng / 2) ** 2
    return 2 * radius_m * asin(sqrt(a))

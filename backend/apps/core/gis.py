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
        def __init__(self, x, y):
            self.x = x
            self.y = y

        def __str__(self):
            return f"POINT({self.x} {self.y})"

    gis_models = _LocalGisModels()

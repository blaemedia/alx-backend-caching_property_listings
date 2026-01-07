from django.core.cache import cache
from .models import Property


def get_all_properties():
    """
    Fetch all properties from Redis cache or database.
    Cache timeout: 1 hour (3600 seconds)
    """
    queryset = cache.get("all_properties")

    if queryset is None:
        queryset = Property.objects.all()
        cache.set("all_properties", queryset, 3600)

    return queryset

import logging

from django.core.cache import cache
from django_redis import get_redis_connection

from .models import Property

logger = logging.getLogger(__name__)


def get_all_properties():
    queryset = cache.get("all_properties")

    if queryset is None:
        queryset = Property.objects.all()
        cache.set("all_properties", queryset, 3600)

    return queryset


def get_redis_cache_metrics():
    """
    Retrieve Redis cache hit/miss metrics and calculate hit ratio.
    """
    try:
        redis_conn = get_redis_connection("default")
        info = redis_conn.info()

        hits = info.get("keyspace_hits", 0)
        misses = info.get("keyspace_misses", 0)

        total_requests = hits + misses
        hit_ratio = hits / total_requests if total_requests > 0 else 0

        metrics = {
            "keyspace_hits": hits,
            "keyspace_misses": misses,
            "hit_ratio": round(hit_ratio, 4),
        }

        logger.info(
            "Redis cache metrics | hits=%s misses=%s hit_ratio=%s",
            hits,
            misses,
            metrics["hit_ratio"],
        )

        return metrics

    except Exception as exc:
        logger.error("Error retrieving Redis cache metrics: %s", exc)
        return {
            "keyspace_hits": 0,
            "keyspace_misses": 0,
            "hit_ratio": 0,
        }

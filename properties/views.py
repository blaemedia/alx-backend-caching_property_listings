from django.http import JsonResponse
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_GET

from .models import Property


@cache_page(60 * 15)  # Cache for 15 minutes
@require_GET
def property_list(request):
    properties = (
        Property.objects
        .all()
        .values(
            "id",
            "title",
            "description",
            "price",
            "location",
            "created_at",
        )
    )

    return JsonResponse(
        {
            "count": properties.count(),
            "data": list(properties),
        },
        safe=True,
        json_dumps_params={"ensure_ascii": False},
    )

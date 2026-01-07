from django.http import JsonResponse
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_GET
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import json

from .models import Property


@cache_page(60 * 15)  # Cache for 15 minutes
@require_GET
def property_list(request):
    try:
        # Get all properties
        properties = Property.objects.all()
        
        # Get query parameters for filtering (optional)
        location = request.GET.get('location', None)
        min_price = request.GET.get('min_price', None)
        max_price = request.GET.get('max_price', None)
        
        # Apply filters if provided
        if location:
            properties = properties.filter(location__icontains=location)
        if min_price:
            properties = properties.filter(price__gte=min_price)
        if max_price:
            properties = properties.filter(price__lte=max_price)
        
        # Pagination
        page = request.GET.get('page', 1)
        per_page = request.GET.get('per_page', 10)
        
        try:
            per_page = int(per_page)
            per_page = min(max(per_page, 1), 100)  # Limit per_page between 1 and 100
        except ValueError:
            per_page = 10
        
        paginator = Paginator(properties, per_page)
        
        try:
            properties_page = paginator.page(page)
        except PageNotAnInteger:
            properties_page = paginator.page(1)
        except EmptyPage:
            properties_page = paginator.page(paginator.num_pages)
        
        # Prepare data
        data = {
            "count": paginator.count,
            "total_pages": paginator.num_pages,
            "current_page": properties_page.number,
            "per_page": per_page,
            "next": properties_page.has_next(),
            "previous": properties_page.has_previous(),
            "data": list(properties_page.object_list.values(
                "id",
                "title",
                "description",
                "price",
                "location",
                "created_at",
            ))
        }
        
        # Return JSON response
        return JsonResponse(
            data,
            safe=True,
            json_dumps_params={"ensure_ascii": False},
        )
        
    except Exception as e:
        # Handle any unexpected errors
        return JsonResponse(
            {
                "error": "An error occurred while fetching properties",
                "details": str(e)
            },
            status=500,
            safe=True,
            json_dumps_params={"ensure_ascii": False},
        )
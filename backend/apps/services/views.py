"""
apps/services/views.py
---------------------------------------------------------------
frontend को assets/js/services.js ले यहींबाट JSON तान्छ।
---------------------------------------------------------------
"""
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from . import selectors


def _serialize_service(service):
    return {
        "id": service.id,
        "slug": service.slug,
        "title": service.title,
        "summary": service.summary,
        "icon_emoji": service.icon_emoji,
        "price_note": service.price_note,
    }


@require_http_methods(["GET"])
def service_list_view(request):
    services = selectors.get_active_services()
    return JsonResponse({"results": [_serialize_service(s) for s in services]})

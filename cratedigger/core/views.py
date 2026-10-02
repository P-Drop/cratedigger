from django.http import HttpRequest, JsonResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_safe

from .health import run_checks


@never_cache
@require_safe
def health_check(request: HttpRequest) -> JsonResponse:
    health_status = run_checks()
    is_healthy = all(health_status.values())
    health_response = {
        "status": "healthy" if is_healthy else "unhealthy",
        "checks": {
            service: "up" if status else "down"
            for service, status in health_status.items()
        },
    }
    return JsonResponse(
        health_response,
        status=200 if is_healthy else 503,
    )

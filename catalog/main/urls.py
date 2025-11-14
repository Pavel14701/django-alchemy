from django.http import JsonResponse
from django.urls import path
from products.controllers.views import products_view

urlpatterns = [
    path("products/", products_view),
]


# --- JSON error handlers ---
def error_400(request, exception) -> JsonResponse:
    return JsonResponse({"status": 400, "error": "Bad Request"}, status=400)


def error_401(request, exception=None) -> JsonResponse:
    return JsonResponse({"status": 401, "error": "Unauthorized"}, status=401)


def error_403(request, exception) -> JsonResponse:
    return JsonResponse({"status": 403, "error": "Forbidden"}, status=403)


def error_404(request, exception) -> JsonResponse:
    return JsonResponse({"status": 404, "error": "Not Found"}, status=404)


def error_405(request, exception=None) -> JsonResponse:
    return JsonResponse({"status": 405, "error": "Method Not Allowed"}, status=405)


def error_408(request, exception=None) -> JsonResponse:
    return JsonResponse({"status": 408, "error": "Request Timeout"}, status=408)


def error_429(request, exception=None) -> JsonResponse:
    return JsonResponse({"status": 429, "error": "Too Many Requests"}, status=429)


def error_500(request) -> JsonResponse:
    return JsonResponse({"status": 500, "error": "Internal Server Error"}, status=500)


def error_502(request, exception=None) -> JsonResponse:
    return JsonResponse({"status": 502, "error": "Bad Gateway"}, status=502)


def error_503(request, exception=None) -> JsonResponse:
    return JsonResponse({"status": 503, "error": "Service Unavailable"}, status=503)


def error_504(request, exception=None) -> JsonResponse:
    return JsonResponse({"status": 504, "error": "Gateway Timeout"}, status=504)


# --- Привязка к глобальным хэндлерам ---
handler400 = "main.urls.error_400"
handler403 = "main.urls.error_403"
handler404 = "main.urls.error_404"
handler500 = "main.urls.error_500"

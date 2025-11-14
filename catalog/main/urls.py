from django.http import HttpRequest, JsonResponse
from django.urls import path
from products.controllers.views import products_view

urlpatterns = [
    path("products/", products_view),
]

ERROR_CODES = {
    400: "Bad Request",
    401: "Unauthorized",
    403: "Forbidden",
    404: "Not Found",
    405: "Method Not Allowed",
    408: "Request Timeout",
    429: "Too Many Requests",
    500: "Internal Server Error",
    502: "Bad Gateway",
    503: "Service Unavailable",
    504: "Gateway Timeout",
}

for code, message in ERROR_CODES.items():
    def view(
        request: HttpRequest,
        exception: Exception | None = None,
        status_code: int = code,
        error_message: str = message,
    ) -> JsonResponse:
        return JsonResponse(
            {
                "status": status_code,
                "error": error_message,
            },
            status=status_code,
        )
    globals()[f"error_{code}"] = view

handler400 = "main.urls.error_400"
handler403 = "main.urls.error_403"
handler404 = "main.urls.error_404"
handler500 = "main.urls.error_500"

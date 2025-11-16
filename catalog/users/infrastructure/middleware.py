# middleware.py
from typing import Any

from django.http import JsonResponse

from ..application.errors import ServiceError


class ServiceErrorMiddleware:
    def __init__(self, get_response) -> None:
        self.get_response = get_response

    def __call__(self, request) -> Any | JsonResponse:
        try:
            return self.get_response(request)
        except ServiceError as e:
            return JsonResponse({"error": str(e)}, status=e.status_code)

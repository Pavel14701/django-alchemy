from dataclasses import asdict
from typing import Any, Optional

from django.http import HttpRequest, HttpResponse

from main.application.interfaces import (
    IGuestSessionBackend,
    IRedisSessionBackend,
    SessionData,
)


class SessionService:
    def __init__(
        self, 
        guest_backend: IGuestSessionBackend, 
        auth_backend: IRedisSessionBackend
    ) -> None:
        self._guest_backend = guest_backend
        self._auth_backend = auth_backend

    def _is_authenticated(self, request: HttpRequest) -> bool:
        # простая проверка: есть ли auth_session кука
        return "auth_session" in request.COOKIES

    def get_data(self, request: HttpRequest) -> Optional[dict[str, Any]]:
        if not self._is_authenticated(request):
            return self._guest_backend.read(request)
        session = self._auth_backend.read(request)
        return asdict(session) if session else None

    def set_data(
        self, 
        request: HttpRequest, 
        response: HttpResponse, 
        data: dict[str, Any]
    ) -> None:
        if self._is_authenticated(request):
            session = SessionData(**data)
            self._auth_backend.update(request, session, response)
        else:
            self._guest_backend.update(request, data, response)

    def clear(self, request: HttpRequest, response: HttpResponse) -> None:
        if self._is_authenticated(request):
            self._auth_backend.delete(request, response)
        else:
            self._guest_backend.delete(request, response)

    def merge_guest_into_auth(
        self, 
        request: HttpRequest, 
        response: HttpResponse
    ) -> None:
        """При логине переносим данные из гостевой сессии в авторизованную."""
        if guest_data := self._guest_backend.read(request):
            session = SessionData(**guest_data)
            self._auth_backend.update(request, session, response)
            self._guest_backend.delete(request, response)

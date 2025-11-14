import contextlib
from typing import Any, cast
from uuid import UUID

from django.http import HttpRequest, HttpResponse

from main.application.interfaces import (
    IGuestSessionBackend,
    IRedisSessionBackend,
    UUIDGenerator,
)
from main.domain.entities import SessionData


class MiddlewareMeta(type):
    def __call__(cls, get_response, *args, **kwargs) -> Any:
        instance = super().__call__(get_response)
        from container import container
        instance.redis_backend = container.get(IRedisSessionBackend)
        instance.guest_manager = container.get(IGuestSessionBackend)
        instance.uuid_generator = container.get(UUIDGenerator)
        return instance


class SessionMiddleware(metaclass=MiddlewareMeta):
    """
    Кастомный middleware для управления аутентифицированными и гостевыми сессиями.
    """

    redis_backend: IRedisSessionBackend
    guest_manager: IGuestSessionBackend
    uuid_generator: UUIDGenerator

    def __init__(self, get_response) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        self._ensure_session_dict(request)
        session_id = self._extract_session_id(request)
        session_data = self._load_session_data(request, session_id)
        response: HttpResponse = self.get_response(request)
        if "session_data" not in request.session:
            self._create_guest_session(request, response, session_id)
        if session_data:
            self._cleanup_guest_session(request, response)
        return response

    def _ensure_session_dict(self, request: HttpRequest) -> None:
        if not hasattr(request, "session"):
            request.session = cast(Any, {})

    def _extract_session_id(self, request: HttpRequest) -> str | None:
        return request.COOKIES.get(
            "auth_session"
        ) or request.COOKIES.get(
            "guest_session"
        )

    def _load_session_data(
        self, 
        request: HttpRequest, 
        session_id: str | None
    ) -> SessionData | None:
        if not session_id:
            return None
        with contextlib.suppress(ValueError):
            session_uuid = UUID(session_id)
            session_data = self.redis_backend.read(request)
            request.session["session_data"] = session_data or str(session_uuid)
            return session_data
        return None

    def _create_guest_session(
        self, 
        request: HttpRequest, 
        response: HttpResponse, 
        session_id: str | None
    ) -> None:
        if session_id:
            try:
                guest_session_id = UUID(session_id)
            except ValueError:
                guest_session_id = self.uuid_generator()
        else:
            guest_session_id = self.uuid_generator()
        guest_session = self.guest_manager.create(
            id=guest_session_id,
            data={},
            response=response,
        )
        request.session["session_data"] = str(guest_session)
        response.set_cookie(
            key="guest_session",
            value=str(guest_session),
            httponly=True,
        )

    def _cleanup_guest_session(
        self, 
        request: HttpRequest, 
        response: HttpResponse
    ) -> None:
        self.guest_manager.delete(request, response)

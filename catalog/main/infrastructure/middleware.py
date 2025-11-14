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
        sid, data = self._load_or_init_session(request)
        response: HttpResponse = self.get_response(request)
        self._sync_guest_session(request, response, sid, data)
        return response

    def _load_or_init_session(
        self, 
        request: HttpRequest
    ) -> tuple[str | None, SessionData | None]:
        if not hasattr(request, "session"):
            request.session = cast(Any, {})

        sid = request.COOKIES.get(
            "auth_session"
        ) or request.COOKIES.get(
            "guest_session"
        )
        data: SessionData | None = None

        if sid:
            with contextlib.suppress(ValueError):
                uuid_ = UUID(sid)
                data = self.redis_backend.read(request)
                request.session["session_data"] = data or str(uuid_)

        return sid, data

    def _sync_guest_session(
        self,
        request: HttpRequest,
        response: HttpResponse,
        sid: str | None,
        data: SessionData | None
    ) -> None:
        if "session_data" not in request.session:
            guest_id = self.uuid_generator()
            with contextlib.suppress(ValueError, TypeError):
                guest_id = UUID(sid) if sid else guest_id

            guest = self.guest_manager.create(id=guest_id, data={}, response=response)
            request.session["session_data"] = str(guest)
            response.set_cookie("guest_session", str(guest), httponly=True)

        elif data and "auth_session" in request.COOKIES:
            # если есть авторизованная сессия → чистим гостевую
            self.guest_manager.delete(request, response)
            response.delete_cookie("guest_session")

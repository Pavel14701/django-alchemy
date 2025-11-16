import contextlib
from typing import cast
from uuid import UUID

from django.contrib.sessions.backends.base import SessionBase
from django.http import HttpResponse

from catalog.main.infrastructure.sessions import CustomSession
from main.application.interfaces import (
    GuestSessionBackendProtocol,
    UserSessionBackendProtocol,
    UUIDGenerator,
)
from main.domain.entities import SessionData

from ..integrations import DishkaRequest


class MiddlewareMeta(type):
    def __call__(cls, get_response, *args, **kwargs):
        instance = super().__call__(get_response)
        from container import container
        instance.redis_backend = container.get(UserSessionBackendProtocol)
        instance.guest_manager = container.get(GuestSessionBackendProtocol)
        instance.uuid_generator = container.get(UUIDGenerator)
        return instance


class SessionMiddleware(metaclass=MiddlewareMeta):
    """
    Кастомный middleware для управления аутентифицированными и гостевыми сессиями.
    """

    redis_backend: UserSessionBackendProtocol
    guest_manager: GuestSessionBackendProtocol
    uuid_generator: UUIDGenerator

    def __init__(self, get_response) -> None:
        self.get_response = get_response

    def __call__(self, request: DishkaRequest) -> HttpResponse:
        sid, data = self._load_or_init_session(request)
        response: HttpResponse = self.get_response(request)
        self._sync_guest_session(request, response, sid, data)
        return response

    def _load_or_init_session(
        self,
        request: DishkaRequest
    ) -> tuple[UUID, SessionData]:
        sid: UUID = self.uuid_generator()
        data: SessionData | None = None

        if sid_hex := request.COOKIES.get("auth_session") or request.COOKIES.get(
            "guest_session"
        ):
            with contextlib.suppress(ValueError):
                sid = UUID(sid_hex)
                data = self.redis_backend.read(sid)

        if not data:
            data = SessionData(user_id=sid, data={})
            self.redis_backend.create(sid, data)

        request.session = cast(
            SessionBase, 
            CustomSession(sid, data, self.redis_backend)
        )
        return sid, data

    def _sync_guest_session(
        self,
        request: DishkaRequest,
        response: HttpResponse,
        sid: UUID | None,
        data: SessionData | None
    ) -> None:
        if "session_data" not in request.session:
            guest_id = self.uuid_generator()
            with contextlib.suppress(ValueError, TypeError):
                guest_id = sid or guest_id

            self.guest_manager.create(guest_id, {})
            request.session["session_data"] = str(guest_id)
            response.set_cookie("guest_session", guest_id.hex, httponly=True)

        elif data and "auth_session" in request.COOKIES:
            if sid:
                self.guest_manager.delete(sid)
            response.delete_cookie("guest_session")

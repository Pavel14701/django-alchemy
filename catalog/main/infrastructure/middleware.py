import contextlib
from typing import Any
from uuid import UUID

from django.http import HttpRequest, HttpResponse

from main.application.interfaces import (
    IGuestSessionBackend,
    IRedisSessionBackend,
)
from main.domain.entities import SessionData


class MiddlewareMeta(type):
    def __call__(cls, get_response, *args, **kwargs) -> Any:
        instance = super().__call__(get_response)
        from container import container
        instance.redis_backend = container.get(IRedisSessionBackend)
        instance.guest_manager = container.get(IGuestSessionBackend)
        return instance


class SessionMiddleware(metaclass=MiddlewareMeta):
    """
    Django middleware для управления аутентифицированными и гостевыми сессиями.
    """

    redis_backend: IRedisSessionBackend
    guest_manager: IGuestSessionBackend

    def __init__(
        self,
        get_response,
    ) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """
        Основной цикл middleware:
        - достаём session_id из cookies
        - проверяем Redis
        - создаём гостевую сессию при необходимости
        - чистим guest_session если есть auth_session
        """
        session_id = request.COOKIES.get(
            "auth_session"
        ) or request.COOKIES.get(
            "guest_session"
        )
        session_data: SessionData | None = None
        if session_id:
            with contextlib.suppress(ValueError):
                session_uuid = UUID(session_id)
                session_data = self.redis_backend.read(request)
                request.session["session_data"] = session_data or str(session_uuid)
        response: HttpResponse = self.get_response(request)
        if "session_data" not in request.session:
            guest_session_id = UUID(session_id) if session_id else UUID(int=0)
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
        if session_data:
            self.guest_manager.delete(request, response)
        return response

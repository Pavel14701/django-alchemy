import contextlib
from uuid import UUID

from django.http import HttpRequest, HttpResponse

from main.domain.entities import SessionData
from main.infrastructure.sessions import GuestSessionBackend, RedisSessionBackend


class SessionMiddleware:
    """
    Django middleware для управления аутентифицированными и гостевыми сессиями.
    """

    def __init__(
        self,
        get_response,
        redis_manager: RedisSessionBackend,
        guest_manager: GuestSessionBackend,
    ):
        self.get_response = get_response
        self.redis_backend = redis_manager
        self.guest_manager = guest_manager

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

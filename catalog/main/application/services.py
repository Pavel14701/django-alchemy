from dataclasses import asdict
from typing import Any, Optional
from uuid import UUID

from django.http import HttpRequest, HttpResponse

from main.application.interfaces import (
    GuestSessionBackendProtocol,
    SessionData,
    UserSessionBackendProtocol,
)


class SessionService:
    def __init__(
        self,
        guest_backend: GuestSessionBackendProtocol,
        auth_backend: UserSessionBackendProtocol,
    ) -> None:
        self._guest_backend = guest_backend
        self._auth_backend = auth_backend

    def _get_auth_session_id(self, request: HttpRequest) -> Optional[UUID]:
        sid = request.COOKIES.get("auth_session")
        return UUID(sid) if sid else None

    def _get_guest_session_id(self, request: HttpRequest) -> Optional[UUID]:
        sid = request.COOKIES.get("guest_session")
        return UUID(sid) if sid else None

    def _is_authenticated(self, request: HttpRequest) -> bool:
        return "auth_session" in request.COOKIES

    def get_data(self, request: HttpRequest) -> Optional[dict[str, Any]]:
        if not self._is_authenticated(request):
            if sid := self._get_guest_session_id(request):
                return self._guest_backend.read(sid)
            return None
        if sid := self._get_auth_session_id(request):
            session = self._auth_backend.read(sid)
            return asdict(session) if session else None
        return None

    def set_data(
        self,
        request: HttpRequest,
        response: HttpResponse,
        data: dict[str, Any],
    ) -> None:
        if self._is_authenticated(request):
            if sid := self._get_auth_session_id(request):
                session = SessionData(**data)
                self._auth_backend.update(sid, session)
        elif sid := self._get_guest_session_id(request):
            self._guest_backend.update(sid, data)

    def clear(self, request: HttpRequest, response: HttpResponse) -> None:
        if self._is_authenticated(request):
            if sid := self._get_auth_session_id(request):
                self._auth_backend.delete(sid)
            response.delete_cookie("auth_session")
        else:
            if sid := self._get_guest_session_id(request):
                self._guest_backend.delete(sid)
            response.delete_cookie("guest_session")

    def merge_guest_into_auth(
        self,
        request: HttpRequest,
        response: HttpResponse,
    ) -> None:
        """При логине переносим данные из гостевой сессии в авторизованную."""
        guest_sid = self._get_guest_session_id(request)
        auth_sid = self._get_auth_session_id(request)

        if guest_sid and auth_sid:
            if guest_data := self._guest_backend.read(guest_sid):
                session = SessionData(**guest_data)
                self._auth_backend.update(auth_sid, session)
                self._guest_backend.delete(guest_sid)
                response.delete_cookie("guest_session")

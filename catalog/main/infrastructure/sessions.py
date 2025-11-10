import json
from dataclasses import asdict
from typing import Any, Optional, cast
from uuid import UUID, uuid4

from django.http import HttpRequest, HttpResponse
from redis import Redis  # синхронный клиент

from main.application.interfaces import IGuestSessionBackend, ISessionBackend
from main.domain.entities import SessionData
from main.infrastructure.cookies import CookieRepo


class RedisSessionBackend(ISessionBackend[UUID, SessionData]):
    """Manages session storage in Redis (sync version)."""

    def __init__(self, redis: Redis) -> None:
        self._redis = redis

    def create(self, session_id: UUID, data: SessionData) -> None:
        """Creates a new session in Redis."""
        self._redis.set(
            name=session_id.hex,
            value=json.dumps(asdict(data)),
            ex=3600
        )

    def read(self, session_id: UUID) -> Optional[SessionData]:
        session_data = cast(Optional[bytes], self._redis.get(session_id.hex))
        if session_data is None:
            return None
        return SessionData(**json.loads(session_data.decode("utf-8")))

    def delete(self, session_id: UUID) -> None:
        """Deletes a session from Redis."""
        self._redis.delete(session_id.hex)


class GuestSessionBackend(IGuestSessionBackend[UUID, dict[str, Any]]):
    """Handles guest session management using CookieManager (sync version)."""

    def __init__(self, cookie_manager: CookieRepo) -> None:
        self._cookie_manager = cookie_manager

    def create_guest_session(self, response: HttpResponse) -> UUID:
        """Creates a new guest session."""
        session_id = uuid4()
        self._cookie_manager.set_cookie(
            response=response,
            key=self._cookie_manager.GUEST_COOKIE,
            value=str(session_id)
        )
        return session_id

    def get_guest_session(self, request: HttpRequest) -> Optional[UUID]:
        """Retrieves the current guest session."""
        session_id = self._cookie_manager.get_cookie(
            request=request,
            key=self._cookie_manager.GUEST_COOKIE
        )
        return UUID(session_id) if session_id else None

    def delete_guest_session(self, response: HttpResponse) -> None:
        """Deletes the guest session."""
        self._cookie_manager.delete_cookie(
            response=response,
            key=self._cookie_manager.GUEST_COOKIE
        )
        self._cookie_manager.delete_cookie(
            response=response,
            key=self._cookie_manager.DATA_COOKIE
        )

    def update_guest_data(
        self,
        request: HttpRequest,
        response: HttpResponse,
        new_data: dict[str, Any]
    ) -> None:
        """Updates guest data while preserving existing information."""
        raw_data = self._cookie_manager.get_cookie(
            request=request,
            key=self._cookie_manager.DATA_COOKIE
        )
        # raw_data: str | None → json.loads принимает str
        current_data: dict[str, Any] = json.loads(raw_data) if raw_data else {}
        current_data.update(new_data)
        self._cookie_manager.set_cookie(
            response=response,
            key=self._cookie_manager.DATA_COOKIE,
            value=json.dumps(current_data)
        )

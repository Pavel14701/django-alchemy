import json
from dataclasses import asdict
from typing import Any, Optional, cast
from uuid import UUID

from django.http import HttpRequest, HttpResponse
from redis import Redis

from main.application.interfaces import (
    IGuestSessionBackend,
    IRedisSessionBackend,
)
from main.domain.entities import SessionData


class RedisSessionBackend(IRedisSessionBackend):
    """Управление авторизованными сессиями в Redis (синхронная версия)."""

    def __init__(self, redis: Redis) -> None:
        self._redis: Redis = redis

    def create(self, id: UUID, data: SessionData, response: HttpResponse) -> UUID:
        """Создать новую сессию в Redis и записать идентификатор в куки."""
        self._redis.set(
            name=id.hex,
            value=json.dumps(asdict(data)),
            ex=3600  # TTL 1 час
        )
        response.set_cookie("auth_session", id.hex, httponly=True)
        return id

    def read(self, request: HttpRequest) -> Optional[SessionData]:
        session_id = request.COOKIES.get("auth_session")
        if not session_id:
            return None
        session_data = cast(Optional[bytes], self._redis.get(session_id))
        if session_data is None:
            return None
        return SessionData(**json.loads(session_data.decode("utf-8")))

    def update(
        self, 
        request: HttpRequest, 
        data: SessionData, 
        response: HttpResponse
    ) -> None:
        if session_id := request.COOKIES.get("auth_session"):
            self._redis.set(session_id, json.dumps(asdict(data)), ex=3600)

    def delete(self, request: HttpRequest, response: HttpResponse) -> None:
        if session_id := request.COOKIES.get("auth_session"):
            self._redis.delete(session_id)
        response.delete_cookie("auth_session")


class GuestSessionBackend(IGuestSessionBackend):
    """Управление гостевыми сессиями в Redis."""

    COOKIE_NAME = "guest_session"

    def __init__(self, redis: Redis) -> None:
        self._redis = redis

    def create(self, id: UUID, data: dict[str, Any], response: HttpResponse) -> UUID:
        """Создать гостевую сессию в Redis и записать идентификатор в куки."""
        self._redis.set(
            name=id.hex,
            value=json.dumps(data),
            ex=1800
        )
        response.set_cookie(self.COOKIE_NAME, id.hex, httponly=True)
        return id

    def read(self, request: HttpRequest) -> Optional[dict[str, Any]]:
        session_id = request.COOKIES.get(self.COOKIE_NAME)
        if not session_id:
            return None
        raw_data = cast(Optional[bytes], self._redis.get(session_id))
        return None if raw_data is None else json.loads(raw_data.decode("utf-8"))

    def update(
        self, 
        request: HttpRequest, 
        data: dict[str, Any], 
        response: HttpResponse
    ) -> None:
        if session_id := request.COOKIES.get(self.COOKIE_NAME):
            raw_data = cast(Optional[bytes], self._redis.get(session_id))
            current_data: dict[str, Any] = json.loads(
                raw_data.decode("utf-8")
            ) if raw_data else {}
            current_data |= data
            self._redis.set(session_id, json.dumps(current_data), ex=1800)

    def delete(self, request: HttpRequest, response: HttpResponse) -> None:
        if session_id := request.COOKIES.get(self.COOKIE_NAME):
            self._redis.delete(session_id)
        response.delete_cookie(self.COOKIE_NAME)

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
        self._redis = redis

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
    """Управление гостевыми сессиями через куки."""

    COOKIE_NAME = "guest_session"
    DATA_COOKIE = "guest_data"

    def create(self, id: UUID, data: dict[str, Any], response: HttpResponse) -> UUID:
        response.set_cookie(self.COOKIE_NAME, str(id), httponly=True)
        response.set_cookie(self.DATA_COOKIE, json.dumps(data), httponly=True)
        return id

    def read(self, request: HttpRequest) -> Optional[dict[str, Any]]:
        raw_data = request.COOKIES.get(self.DATA_COOKIE)
        return json.loads(raw_data) if raw_data else None

    def update(
        self, 
        request: HttpRequest, 
        data: dict[str, Any], 
        response: HttpResponse
    ) -> None:
        raw_data = request.COOKIES.get(self.DATA_COOKIE)
        current_data: dict[str, Any] = json.loads(raw_data) if raw_data else {}
        current_data |= data
        response.set_cookie(self.DATA_COOKIE, json.dumps(current_data), httponly=True)

    def delete(self, request: HttpRequest, response: HttpResponse) -> None:
        if request.COOKIES.get(self.COOKIE_NAME):
            response.delete_cookie(self.COOKIE_NAME)
        if request.COOKIES.get(self.DATA_COOKIE):
            response.delete_cookie(self.DATA_COOKIE)

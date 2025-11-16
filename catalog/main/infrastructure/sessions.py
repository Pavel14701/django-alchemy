import json
from dataclasses import asdict
from typing import Any, Optional, cast
from uuid import UUID

from django.contrib.sessions.backends.base import SessionBase
from redis import Redis

from main.application.interfaces import (
    GuestSessionBackendProtocol,
    SessionStorageProtocol,
    UserSessionBackendProtocol,
)
from main.domain.entities import SessionData


class RedisSessionBackend(UserSessionBackendProtocol):
    """Управление авторизованными сессиями в Redis."""

    def __init__(self, redis: Redis) -> None:
        self._redis = redis

    def create(self, id: UUID, data: SessionData) -> UUID:
        self._redis.set(id.hex, json.dumps(asdict(data)), ex=3600)
        return id

    def read(self, id: UUID) -> Optional[SessionData]:
        raw = cast(Optional[bytes], self._redis.get(id.hex))
        return None if raw is None else SessionData(**json.loads(raw.decode("utf-8")))

    def update(self, id: UUID, data: SessionData) -> None:
        self._redis.set(id.hex, json.dumps(asdict(data)), ex=3600)

    def delete(self, id: UUID) -> None:
        self._redis.delete(id.hex)


class GuestSessionBackend(GuestSessionBackendProtocol):
    """Управление гостевыми сессиями в Redis."""

    def __init__(self, redis: Redis) -> None:
        self._redis = redis

    def create(self, id: UUID, data: dict[str, Any]) -> UUID:
        self._redis.set(id.hex, json.dumps(data), ex=1800)
        return id

    def read(self, id: UUID) -> Optional[dict[str, Any]]:
        raw = cast(Optional[bytes], self._redis.get(id.hex))
        return None if raw is None else json.loads(raw.decode("utf-8"))

    def update(self, id: UUID, data: dict[str, Any]) -> None:
        raw = cast(Optional[bytes], self._redis.get(id.hex))
        current: dict[str, Any] = json.loads(raw.decode("utf-8")) if raw else {}
        current |= data
        self._redis.set(id.hex, json.dumps(current), ex=1800)

    def delete(self, id: UUID) -> None:
        self._redis.delete(id.hex)


class CustomSession(SessionBase):
    def __init__(
        self, 
        session_id: UUID, 
        session_data: SessionData, 
        backend: SessionStorageProtocol
    ) -> None:
        super().__init__()
        self.session_id = session_id
        self._session_data = session_data
        self.backend = backend
        self.modified = False

    def __getitem__(self, key) -> Any:
        return self._session_data.data[key]

    def __setitem__(self, key, value) -> None:
        self._session_data.data[key] = value
        self.modified = True

    def __delitem__(self, key) -> None:
        del self._session_data.data[key]
        self.modified = True

    def __contains__(self, key) -> bool:
        return key in self._session_data.data

    def get(self, key, default=None) -> Any | None:
        return self._session_data.data.get(key, default)

    @property
    def session_key(self) -> str:
        return str(self.session_id)

    @property
    def user_id(self) -> UUID:
        return self._session_data.user_id

    @property
    def raw(self) -> SessionData:
        return self._session_data

    def save(self, must_create: bool = False) -> None:
        if self.modified:
            self.backend.update(self.session_id, self._session_data)
            self.modified = False


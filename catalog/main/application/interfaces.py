from typing import Any, Callable, Optional, Protocol, TypeVar
from uuid import UUID

from main.domain.entities import SessionData

UUIDGenerator = Callable[[], UUID]

SID = TypeVar("SID")
SData = TypeVar("SData")


class SessionProtocol(Protocol):
    """Интерфейс для управления транзакциями уровня ORM/UnitOfWork."""

    def commit(self) -> None:
        """Зафиксировать изменения в транзакции."""
        raise NotImplementedError()

    def flush(self) -> None:
        """Сбросить изменения без коммита."""
        raise NotImplementedError()

    def rollback(self) -> None:
        """Откатить транзакцию."""
        raise NotImplementedError()


class SessionStorageProtocol(Protocol[SID, SData]):
    """Протокол для работы с сессиями в сторе (Redis, DB и т.д.)."""

    def create(self, id: SID, data: SData) -> SID:
        raise NotImplementedError()

    def read(self, id: SID) -> Optional[SData]:
        raise NotImplementedError()

    def update(self, id: SID, data: SData) -> None:
        raise NotImplementedError()

    def delete(self, id: SID) -> None:
        raise NotImplementedError()


class UserSessionBackendProtocol(SessionStorageProtocol[UUID, SessionData]):
    ...


class GuestSessionBackendProtocol(SessionStorageProtocol[UUID, dict[str, Any]]):
    ...

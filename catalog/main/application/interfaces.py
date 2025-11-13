from typing import Any, Callable, Optional, Protocol, TypeVar
from uuid import UUID

from django.http import HttpRequest, HttpResponse

from main.domain.entities import SessionData

UUIDGenerator = Callable[[], UUID]

SID = TypeVar("SID")
SData = TypeVar("SData")


class ISession(Protocol):
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


class SessionStorage(Protocol[SID, SData]):
    """
    Единый протокол для работы с сессиями (CRUD + куки).
    Реализации могут быть на Redis, в базе или через куки.
    """

    def create(self, id: SID, data: SData, response: HttpResponse) -> SID:
        """Создать новую сессию и вернуть её идентификатор."""
        raise NotImplementedError()

    def read(self, request: HttpRequest) -> Optional[SData]:
        """Прочитать данные сессии из запроса/хранилища."""
        raise NotImplementedError()

    def update(self, request: HttpRequest, data: SData, response: HttpResponse) -> None:
        """Обновить данные сессии."""
        raise NotImplementedError()

    def delete(self, request: HttpRequest, response: HttpResponse) -> None:
        """Удалить сессию из хранилища и очистить куки."""
        raise NotImplementedError()


class IRedisSessionBackend(SessionStorage[UUID, SessionData]):
    ...


class IGuestSessionBackend(SessionStorage[UUID, dict[str, Any]]):
    ...

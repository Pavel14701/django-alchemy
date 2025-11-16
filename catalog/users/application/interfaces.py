from typing import Optional, Protocol
from uuid import UUID

from ..domain.entities import UserDomain


class UserRepositoryProtocol(Protocol):
    # --- CREATE ---
    def create(self, user: UserDomain) -> UserDomain:
        """Создать нового пользователя и вернуть доменную модель"""
        raise NotImplementedError()

    # --- READ ---
    def read(
        self,
        user_id: Optional[UUID] = None,
        username: Optional[str] = None,
        email: Optional[str] = None,
    ) -> Optional[UserDomain]:
        """Прочитать пользователя по user_id, username или email"""
        raise NotImplementedError()

    def get_by_credentials(
        self, username: Optional[str], email: Optional[str]
    ) -> Optional[UserDomain]:
        """Получить пользователя по username или email (без проверки пароля)"""
        raise NotImplementedError()

    # --- UPDATE ---
    def update(self, user_id: UUID, new_data: UserDomain) -> Optional[UserDomain]:
        """Обновить пользователя по user_id и вернуть обновлённую доменную модель"""
        raise NotImplementedError()

    # --- DELETE ---
    def delete(self, user_id: UUID) -> Optional[UserDomain]:
        """Удалить пользователя по user_id и вернуть удалённую доменную модель"""
        raise NotImplementedError()

    def all_clients(self) -> list[UserDomain]:
        """Вернуть список всех клиентов"""
        raise NotImplementedError()


class PasswordHasherProtocol(Protocol):
    def hash(self, password: str) -> str:
        raise NotImplementedError()

    def verify(self, hashed: str, password: str) -> bool:
        raise NotImplementedError()


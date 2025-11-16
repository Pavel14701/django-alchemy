import datetime
from uuid import UUID

from sqlalchemy.orm import Session

from users.application.interfaces import UserRepositoryProtocol

from ..domain.entities import UserDomain, UserRole, UserStatus
from .models import User


class UserRepository(UserRepositoryProtocol):
    def __init__(self, session: Session) -> None:
        self._session = session

    def _to_entity(self, model: User) -> UserDomain:
        return UserDomain(
            user_id=model.user_id,
            username=model.username,
            email=model.email,
            password_hash=model.password_hash,
            role=UserRole(model.role.value),
            status=UserStatus(model.status.value),
            created_at=model.created_at,
            deleted_at=model.deleted_at,
        )

    def _commit_and_return(self, model: User) -> UserDomain:
        """Общий метод для сохранения изменений и возврата доменной модели."""
        self._session.commit()
        self._session.refresh(model)
        return self._to_entity(model)

    # --- Создание ---
    def create(self, user: UserDomain) -> UserDomain:
        model = User(
            user_id=user.user_id,
            username=user.username,
            email=user.email,
            password_hash=user.password_hash,
            role=user.role,
            status=user.status,
            created_at=user.created_at or datetime.datetime.now(datetime.timezone.utc),
            deleted_at=user.deleted_at,
        )
        self._session.add(model)
        return self._commit_and_return(model)

    # --- Чтение ---
    def read(
        self,
        user_id: UUID | None = None,
        username: str | None = None,
        email: str | None = None,
    ) -> UserDomain | None:
        query = self._session.query(User)
        if user_id:
            model = query.filter(User.user_id == user_id).first()
        elif username:
            model = query.filter(User.username == username).first()
        elif email:
            model = query.filter(User.email == email).first()
        else:
            return None
        return self._to_entity(model) if model else None

    def get_by_credentials(
        self, username: str | None, email: str | None
    ) -> UserDomain | None:
        query = self._session.query(User)
        if username:
            user = query.filter(User.username == username).first()
        elif email:
            user = query.filter(User.email == email).first()
        else:
            return None
        return self._to_entity(user) if user else None

    # --- Обновление ---
    def update(self, user_id: UUID, new_data: UserDomain) -> UserDomain | None:
        model = self._session.query(User).filter(User.user_id == user_id).first()
        if not model:
            return None

        model.username = new_data.username
        model.email = new_data.email
        model.password_hash = new_data.password_hash
        model.role = new_data.role
        model.status = new_data.status
        model.deleted_at = new_data.deleted_at

        return self._commit_and_return(model)

    # --- Удаление ---
    def delete(self, user_id: UUID) -> UserDomain | None:
        model = self._session.query(User).filter(User.user_id == user_id).first()
        if not model:
            return None

        self._session.delete(model)
        self._session.commit()
        return self._to_entity(model)

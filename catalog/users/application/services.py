import datetime
from typing import cast
from uuid import UUID

from redis import Redis

from catalog.main.application.interfaces import UUIDGenerator

from ..domain.entities import UserDomain, UserRole, UserStatus
from .errors import (
    AuthError,
    BlockedError,
    ConflictError,
    InternalError,
    NotFoundError,
    PermissionDenied,
)
from .interfaces import PasswordHasherProtocol, UserRepositoryProtocol


class AccountService:
    def __init__(
        self, 
        repo: UserRepositoryProtocol, 
        redis_client: Redis,
        password_hasher: PasswordHasherProtocol,
        uuid_generator: UUIDGenerator
    ) -> None:
        self._repo = repo
        self._redis = redis_client
        self._password_hasher = password_hasher
        self._uuid_generator = uuid_generator

    # --- Регистрация ---
    def register_user(self, username: str, email: str, password: str) -> UserDomain:
        new_uuid = self._uuid_generator()
        domain_user = UserDomain(
            user_id=new_uuid,
            username=username,
            email=email,
            password_hash=self._password_hasher.hash(password),
            role=UserRole.CLIENT,
            status=UserStatus.PENDING,
        )
        try:
            return self._repo.create(domain_user)
        except ConflictError:
            raise PermissionDenied("Email или username уже заняты")
        except InternalError:
            raise InternalError("Ошибка при регистрации пользователя")

    # --- Авторизация ---
    def authenticate(
        self, 
        username: str | None, 
        email: str | None, 
        password: str
    ) -> UserDomain:
        key = f"login_attempts:{username or email}"
        if self._redis.get(f"blocked:{key}"):
            raise BlockedError()

        user = self._repo.get_by_credentials(username, email)
        if not user:
            raise AuthError("Пользователь не найден")

        if not self._password_hasher.verify(user.password_hash, password):
            attempts = int(cast(str, self._redis.incr(key)))
            self._redis.expire(key, 600)
            if attempts >= 3:
                self._redis.setex(f"blocked:{key}", 900, 1)
                raise BlockedError("Слишком много попыток входа")
            raise AuthError("Неверные учетные данные")

        if user.status == UserStatus.SUSPENDED:
            raise BlockedError("Аккаунт заблокирован")

        self._redis.delete(key)
        return user

    # --- Управление статусами ---
    def activate(self, user_id: UUID) -> UserDomain:
        user = self._repo.read(user_id)
        if not user:
            raise NotFoundError("Пользователь не найден")
        if user.status not in (UserStatus.PENDING, UserStatus.SUSPENDED):
            raise PermissionDenied("Пользователь уже активен или недоступен")
        user.status = UserStatus.ACTIVE
        if updated := self._repo.update(user_id, user):
            return updated
        else:
            raise NotFoundError("Не удалось активировать пользователя")

    def suspend(self, requester_id: UUID, target_username: str) -> UserDomain:
        # проверяем инициатора
        requester = self._repo.read(user_id=requester_id)
        if not requester:
            raise NotFoundError("Запрашивающий пользователь не найден")
        if requester.role != UserRole.ADMIN:
            raise PermissionDenied("Только админ может блокировать пользователей")

        # проверяем цель по username
        user = self._repo.read(username=target_username)
        if not user:
            raise NotFoundError("Пользователь не найден")
        if user.status != UserStatus.ACTIVE:
            raise PermissionDenied("Можно блокировать только активных пользователей")

        user.status = UserStatus.SUSPENDED
        if updated := self._repo.update(user.user_id, user):
            return updated
        raise NotFoundError("Не удалось заблокировать пользователя")

    def unsuspend(self, requester_id: UUID, target_username: str) -> UserDomain:
        # проверяем инициатора
        requester = self._repo.read(user_id=requester_id)
        if not requester:
            raise NotFoundError("Запрашивающий пользователь не найден")
        if requester.role != UserRole.ADMIN:
            raise PermissionDenied("Только админ может разблокировать пользователей")

        # проверяем цель по username
        user = self._repo.read(username=target_username)
        if not user:
            raise NotFoundError("Пользователь не найден")
        if user.status != UserStatus.SUSPENDED:
            raise PermissionDenied(
                "Можно разблокировать только заблокированных пользователей"
            )

        user.status = UserStatus.ACTIVE
        if updated := self._repo.update(user.user_id, user):
            return updated
        raise NotFoundError("Не удалось разблокировать пользователя")

    # --- Удаление / восстановление ---
    def delete(self, user_id: UUID) -> UserDomain:
        user = self._repo.read(user_id)
        if not user:
            raise NotFoundError("Пользователь не найден")
        if user.role == UserRole.CLIENT:
            user.status = UserStatus.DELETED
            user.deleted_at = datetime.datetime.now(datetime.timezone.utc)
            if updated := self._repo.update(user_id, user):
                return updated
            else:
                raise NotFoundError("Не удалось удалить клиента")
        elif deleted := self._repo.delete(user_id):
            return deleted
        else:
            raise NotFoundError("Не удалось удалить пользователя")

    def restore(
        self, 
        username: str | None, 
        email: str | None, 
        password: str
    ) -> UserDomain:
        # ищем пользователя по логину или почте
        user = self._repo.get_by_credentials(username, email)
        if not user or not self._password_hasher.verify(user.password_hash, password):
            raise AuthError("Неверные данные для восстановления")

        if user.role != UserRole.CLIENT or user.status != UserStatus.DELETED:
            raise PermissionDenied("Восстановление недоступно")

        user.status = UserStatus.ACTIVE
        user.deleted_at = None
        if updated := self._repo.update(user.user_id, user):
            return updated
        else:
            raise NotFoundError("Не удалось восстановить пользователя")

    def purge_deleted(self, days: int = 30) -> int:
        cutoff = datetime.datetime.now(
            datetime.timezone.utc
        ) - datetime.timedelta(
            days=days
        )
        users = [
            u for u in self._repo.all_clients()
            if u.status == UserStatus.DELETED and u.deleted_at and u.deleted_at < cutoff
        ]
        for u in users:
            self._repo.delete(u.user_id)
        return len(users)

    # --- Смена роли ---
# --- Смена роли ---
    def change_role(
        self,
        requester_id: UUID,
        target_username: str | None = None,
        target_email: str | None = None,
        new_role: UserRole = UserRole.CLIENT,
    ) -> UserDomain:
        requester = self._repo.read(user_id=requester_id)
        if not requester:
            raise NotFoundError("Запрашивающий пользователь не найден")
        if requester.role == UserRole.CLIENT:
            raise PermissionDenied("Клиент не может менять роли")
        # проверяем, что хотя бы один параметр цели задан
        if not target_username and not target_email:
            raise PermissionDenied("Не указан ни username, ни email для цели")
        target = None
        if target_username:
            target = self._repo.read(username=target_username)
        else:
            target = self._repo.read(email=target_email)
        if not target or target.status == UserStatus.DELETED:
            raise NotFoundError("Пользователь не найден или удалён")
        target.role = new_role
        if updated := self._repo.update(target.user_id, target):
            return updated
        else:
            raise NotFoundError("Не удалось сменить роль")

    # --- Смена пароля ---
    def change_password(
        self, 
        user_id: UUID, 
        old_hash: str, 
        new_hash: str
    ) -> UserDomain:
        user = self._repo.read(user_id)
        if not user:
            raise NotFoundError("Пользователь не найден")
        if user.password_hash != old_hash:
            raise AuthError("Старый пароль неверен")
        user.password_hash = new_hash
        if updated := self._repo.update(user_id, user):
            return updated
        else:
            raise NotFoundError("Не удалось обновить пароль")

    # --- Смена username ---
    def change_username(self, user_id: UUID, new_username: str) -> UserDomain:
        user = self._repo.read(user_id)
        if not user:
            raise NotFoundError("Пользователь не найден")
        user.username = new_username
        if updated := self._repo.update(user_id, user):
            return updated
        else:
            raise NotFoundError("Не удалось сменить username")

    # --- Смена email ---
    def change_email(self, user_id: UUID, new_email: str) -> UserDomain:
        user = self._repo.read(user_id)
        if not user:
            raise NotFoundError("Пользователь не найден")
        user.email = new_email
        if updated := self._repo.update(user_id, user):
            return updated
        else:
            raise NotFoundError("Не удалось сменить email")

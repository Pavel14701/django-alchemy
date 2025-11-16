from typing import Optional
from uuid import UUID

from ..domain.entities import UserRole
from .dto import UserDTO
from .services import AccountService


# --- Регистрация ---
class RegisterUser:
    def __init__(self, service: AccountService) -> None:
        self._service = service

    def execute(self, username: str, email: str, password: str) -> UserDTO:
        # интерактор просто делегирует в сервис
        created = self._service.register_user(username, email, password)
        return UserDTO.from_entity(created)


# --- Авторизация ---
class AuthenticateUser:
    def __init__(self, service: AccountService) -> None:
        self._service = service

    def execute(
        self,
        username: Optional[str],
        email: Optional[str],
        password: str
    ) -> UserDTO:
        domain_user = self._service.authenticate(username, email, password)
        return UserDTO.from_entity(domain_user)


# --- Управление статусами ---
class ActivateUser:
    def __init__(self, service: AccountService) -> None:
        self._service = service

    def execute(self, user_id: UUID) -> UserDTO:
        domain_user = self._service.activate(user_id)
        return UserDTO.from_entity(domain_user)


class SuspendUser:
    def __init__(self, service: AccountService) -> None:
        self._service = service

    def execute(self, requester: UUID, target_username: str) -> UserDTO:
        domain_user = self._service.suspend(requester, target_username)
        return UserDTO.from_entity(domain_user)


class UnsuspendUser:
    def __init__(self, service: AccountService) -> None:
        self._service = service

    def execute(self, requester: UUID, target_username: str) -> UserDTO:
        domain_user = self._service.unsuspend(requester, target_username)
        return UserDTO.from_entity(domain_user)


# --- Удаление / восстановление ---
class DeleteUser:
    def __init__(self, service: AccountService) -> None:
        self._service = service

    def execute(self, user_id: UUID) -> UserDTO:
        domain_user = self._service.delete(user_id)
        return UserDTO.from_entity(domain_user)


class RestoreUser:
    def __init__(self, service: AccountService) -> None:
        self._service = service

    def execute(
        self, 
        username: Optional[str], 
        email: Optional[str], 
        password: str
    ) -> UserDTO:
        domain_user = self._service.restore(username, email, password)
        return UserDTO.from_entity(domain_user)


# --- Смена роли ---
class ChangeRole:
    def __init__(self, account_service: AccountService) -> None:
        self._account_service = account_service

    def execute(
        self,
        requester: UUID,
        target_username: str,
        new_role: UserRole
    ) -> UserDTO:
        domain_user = self._account_service.change_role(
            requester_id=requester,
            target_username=target_username,
            new_role=new_role,
        )
        return UserDTO.from_entity(domain_user)


# --- Смена пароля ---
class ChangePassword:
    def __init__(self, service: AccountService) -> None:
        self._service = service

    def execute(self, user_id: UUID, old_hash: str, new_hash: str) -> UserDTO:
        domain_user = self._service.change_password(user_id, old_hash, new_hash)
        return UserDTO.from_entity(domain_user)


# --- Смена username ---
class ChangeUsername:
    def __init__(self, service: AccountService) -> None:
        self._service = service

    def execute(self, user_id: UUID, new_username: str) -> UserDTO:
        domain_user = self._service.change_username(user_id, new_username)
        return UserDTO.from_entity(domain_user)


# --- Смена email ---
class ChangeEmail:
    def __init__(self, service: AccountService) -> None:
        self._service = service

    def execute(self, user_id: UUID, new_email: str) -> UserDTO:
        domain_user = self._service.change_email(user_id, new_email)
        return UserDTO.from_entity(domain_user)

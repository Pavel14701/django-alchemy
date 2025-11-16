import re
from dataclasses import dataclass
from typing import Any, Dict, Optional

from adaptix import Retort

retort = Retort()


class ValidationError(Exception):
    def __init__(self, field: str, message: str) -> None:
        self.field = field
        self.message = message
        super().__init__(f"{field}: {message}")

    @classmethod
    def for_field(cls, field: str, message: str) -> "ValidationError":
        return cls(field, message)


# --- Регистрация ---
@dataclass
class UserRegisterSchema:
    username: str
    email: str
    password: str   # пользователь вводит сырой пароль

    @classmethod
    def from_raw(cls, raw: Dict[str, Any]) -> "UserRegisterSchema":
        try:
            obj = retort.load(raw, cls)
        except Exception as e:
            raise ValidationError.for_field("body", str(e))

        # --- Валидация username ---
        if not obj.username.strip():
            raise ValidationError.for_field("username", "Must not be empty")
        if not re.match(r"^[A-Za-z0-9_.-]{3,32}$", obj.username):
            raise ValidationError.for_field(
                "username",
                "Invalid format (3-32 chars, letters, digits, _, ., -)"
            )

        # --- Валидация email ---
        if not obj.email.strip():
            raise ValidationError.for_field("email", "Must not be empty")
        email_regex = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
        if not email_regex.match(obj.email.strip()):
            raise ValidationError.for_field("email", "Invalid email format")

        # --- Валидация пароля ---
        if not obj.password.strip():
            raise ValidationError.for_field("password", "Must not be empty")
        if len(obj.password.strip()) < 8:
            raise ValidationError.for_field(
                "password", 
                "Must be at least 8 characters long"
            )
        # --- Нормализация ---
        obj.username = obj.username.strip()
        obj.email = obj.email.strip().lower()
        obj.password = obj.password.strip()
        return obj


# --- Авторизация ---

@dataclass
class UserAuthSchema:
    username: Optional[str] = None
    email: Optional[str] = None
    password: str = ""

    @classmethod
    def from_raw(cls, raw: Dict[str, Any]) -> "UserAuthSchema":
        try:
            obj = retort.load(raw, cls)
        except Exception as e:
            raise ValidationError.for_field("body", str(e))

        # --- Валидация ---
        if not obj.username and not obj.email:
            raise ValidationError.for_field(
                "credentials",
                "Either username or email must be provided"
            )

        if not obj.password.strip():
            raise ValidationError.for_field("password", "Must not be empty")

        # --- Нормализация ---
        if obj.username:
            obj.username = obj.username.strip()
        if obj.email:
            obj.email = obj.email.strip().lower()
        obj.password = obj.password.strip()

        return obj


# --- Смена пароля ---
@dataclass
class UserPasswordSchema:
    old_hash: str
    new_hash: str

    @classmethod
    def from_raw(cls, raw: Dict[str, Any]) -> "UserPasswordSchema":
        try:
            obj = retort.load(raw, cls)
        except Exception as e:
            raise ValidationError.for_field("body", str(e))

        if not obj.old_hash.strip():
            raise ValidationError.for_field("old_hash", "Must not be empty")
        if not obj.new_hash.strip():
            raise ValidationError.for_field("new_hash", "Must not be empty")
        if obj.old_hash.strip() == obj.new_hash.strip():
            raise ValidationError.for_field(
                "new_hash", 
                "New password must differ from old password"
            )

        obj.old_hash = obj.old_hash.strip()
        obj.new_hash = obj.new_hash.strip()

        return obj


# --- Смена username ---
@dataclass
class UserUpdateUsernameSchema:
    new_username: str

    @classmethod
    def from_raw(cls, raw: Dict[str, Any]) -> "UserUpdateUsernameSchema":
        try:
            obj = retort.load(raw, cls)
        except Exception as e:
            raise ValidationError.for_field("body", str(e))

        if not obj.new_username.strip():
            raise ValidationError.for_field("new_username", "Must not be empty")
        if not re.match(r"^[A-Za-z0-9_.-]{3,32}$", obj.new_username):
            raise ValidationError.for_field(
                "new_username", 
                "Invalid format (3-32 chars, letters, digits, _, ., -)"
            )

        obj.new_username = obj.new_username.strip()
        return obj


# --- Смена email ---
@dataclass
class UserUpdateEmailSchema:
    new_email: str

    @classmethod
    def from_raw(cls, raw: Dict[str, Any]) -> "UserUpdateEmailSchema":
        try:
            obj = retort.load(raw, cls)
        except Exception as e:
            raise ValidationError.for_field("body", str(e))

        if not obj.new_email.strip():
            raise ValidationError.for_field("new_email", "Must not be empty")
        email_regex = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
        if not email_regex.match(obj.new_email.strip()):
            raise ValidationError.for_field("new_email", "Invalid email format")

        obj.new_email = obj.new_email.strip().lower()
        return obj


# --- Смена роли ---
@dataclass
class UserRoleSchema:
    target_username: str
    new_role: str

    @classmethod
    def from_raw(cls, raw: Dict[str, Any]) -> "UserRoleSchema":
        try:
            obj = retort.load(raw, cls)
        except Exception as e:
            raise ValidationError.for_field("body", str(e))

        if not obj.target_username.strip():
            raise ValidationError.for_field("target_username", "Must not be empty")
        if not obj.new_role.strip():
            raise ValidationError.for_field("new_role", "Must not be empty")

        obj.target_username = obj.target_username.strip()
        obj.new_role = obj.new_role.strip().upper()

        return obj


@dataclass
class UserUpdateSchema:
    new_username: Optional[str] = None
    new_email: Optional[str] = None
    old_hash: Optional[str] = None
    new_hash: Optional[str] = None

    @classmethod
    def from_raw(cls, raw: Dict[str, Any]) -> "UserUpdateSchema":
        try:
            obj = retort.load(raw, cls)
        except Exception as e:
            raise ValidationError.for_field("body", str(e))

        # --- Валидация username ---
        if obj.new_username is not None:
            if not obj.new_username.strip():
                raise ValidationError.for_field("new_username", "Must not be empty")
            if not re.match(r"^[A-Za-z0-9_.-]{3,32}$", obj.new_username):
                raise ValidationError.for_field(
                    "new_username",
                    "Invalid format (3-32 chars, letters, digits, _, ., -)",
                )
            obj.new_username = obj.new_username.strip()

        # --- Валидация email ---
        if obj.new_email is not None:
            if not obj.new_email.strip():
                raise ValidationError.for_field("new_email", "Must not be empty")
            email_regex = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
            if not email_regex.match(obj.new_email.strip()):
                raise ValidationError.for_field("new_email", "Invalid email format")
            obj.new_email = obj.new_email.strip().lower()

        # --- Валидация пароля ---
        if obj.old_hash is not None or obj.new_hash is not None:
            if not obj.old_hash or not obj.old_hash.strip():
                raise ValidationError.for_field("old_hash", "Must not be empty")
            if not obj.new_hash or not obj.new_hash.strip():
                raise ValidationError.for_field("new_hash", "Must not be empty")
            if obj.old_hash.strip() == obj.new_hash.strip():
                raise ValidationError.for_field(
                    "new_hash", "New password must differ from old password"
                )
            obj.old_hash = obj.old_hash.strip()
            obj.new_hash = obj.new_hash.strip()

        return obj


@dataclass
class UserRestoreSchema:
    username: Optional[str] = None
    email: Optional[str] = None
    password: str = ""

    @classmethod
    def from_raw(cls, raw: Dict[str, Any]) -> "UserRestoreSchema":
        try:
            obj = retort.load(raw, cls)
        except Exception as e:
            raise ValidationError.for_field("body", str(e))

        if not obj.username and not obj.email:
            raise ValidationError.for_field(
                "credentials", 
                "Either username or email must be provided"
            )

        if not obj.password.strip():
            raise ValidationError.for_field("password", "Must not be empty")
        if len(obj.password.strip()) < 8:
            raise ValidationError.for_field(
                "password", 
                "Must be at least 8 characters long"
            )

        if obj.username:
            obj.username = obj.username.strip()
        if obj.email:
            obj.email = obj.email.strip().lower()
        obj.password = obj.password.strip()

        return obj

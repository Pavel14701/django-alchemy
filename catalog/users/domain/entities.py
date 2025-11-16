import datetime
from dataclasses import dataclass
from enum import Enum
from uuid import UUID


class UserRole(Enum):
    ADMIN = "admin"
    CLIENT = "client"
    EDITOR = "editor"


class UserStatus(Enum):
    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DELETED = "deleted"


@dataclass
class UserDomain:
    user_id: UUID
    username: str
    email: str
    password_hash: str
    role: UserRole
    status: UserStatus
    created_at: datetime.datetime | None = None
    deleted_at: datetime.datetime | None = None

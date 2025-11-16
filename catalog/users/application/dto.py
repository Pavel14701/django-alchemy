import datetime
from typing import Iterable, Optional
from uuid import UUID

import msgspec

from users.domain.entities import UserDomain, UserRole, UserStatus


class UserDTO(msgspec.Struct):
    user_id: int | None | str | UUID
    username: str
    email: str
    role: UserRole
    status: UserStatus
    created_at: datetime.datetime | None
    deleted_at: Optional[datetime.datetime] = None

    @classmethod
    def from_entity(cls, user: UserDomain) -> "UserDTO":
        return cls(
            user_id=user.user_id,
            username=user.username,
            email=user.email,
            role=user.role,
            status=user.status,
            created_at=user.created_at,
            deleted_at=user.deleted_at,
        )

    @classmethod
    def from_iterable(cls, users: Iterable[UserDomain]) -> list["UserDTO"]:
        return [cls.from_entity(u) for u in users]

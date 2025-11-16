import datetime
from uuid import UUID

import sqlalchemy as sa
from main.infrastructure.db import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship

from users.domain.entities import UserRole, UserStatus


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[UUID] = mapped_column(sa.UUID, primary_key=True)
    username: Mapped[str] = mapped_column(sa.String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(sa.String(120), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(sa.String(255), nullable=False)

    role: Mapped[UserRole] = mapped_column(sa.Enum(UserRole), default=UserRole.CLIENT)
    status: Mapped[UserStatus] = mapped_column(
        sa.Enum(UserStatus), default=UserStatus.PENDING
    )
    deleted_at: Mapped[datetime.datetime | None] = mapped_column(
        sa.DateTime, nullable=True, index=True
    )

    created_at: Mapped[datetime.datetime] = mapped_column(
        sa.DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc)
    )

    reviews = relationship(
        "Review", 
        back_populates="user", 
        cascade="all, delete-orphan"
    )

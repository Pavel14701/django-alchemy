from dataclasses import dataclass
from typing import Any
from uuid import UUID


@dataclass
class SessionData:
    user_id: UUID
    data: dict[str, Any]
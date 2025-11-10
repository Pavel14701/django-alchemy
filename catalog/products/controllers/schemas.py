from dataclasses import dataclass
from typing import Any, Dict

from adaptix import Retort

from products.application.types import SORT_FIELDS, SortFields

retort = Retort()


class ValidationError(Exception):
    """
    Единая ошибка валидации для схем.
    Хранит поле и сообщение, чтобы удобно отдавать в JSON.
    """
    def __init__(self, field: str, message: str) -> None:
        self.field = field
        self.message = message
        super().__init__(f"{field}: {message}")

    @classmethod
    def for_field(cls, field: str, message: str) -> "ValidationError":
        return cls(field, message)


@dataclass
class ProductQueryParams:
    page: int = 1
    page_size: int = 20
    sort_by: SortFields | None = None
    descending: bool = False

    @classmethod
    def from_raw(cls, raw: Dict[str, Any]) -> "ProductQueryParams":
        # строгая проверка descending
        val = str(raw.get("descending", "false")).lower()
        if val not in ("true", "false"):
            raise ValidationError.for_field(
                "descending", 
                "Value must be 'true' or 'false'"
            )

        # строгая проверка sort_by через Literal
        sort_by = raw.get("sort_by")
        if sort_by not in (*SORT_FIELDS, None):
            raise ValidationError.for_field("sort_by", f"Invalid sort field: {sort_by}")

        try:
            normalized = {
                "page": int(raw.get("page", 1)),
                "page_size": int(raw.get("page_size", 20)),
                "sort_by": sort_by,
                "descending": val == "true",
            }
            return retort.load(normalized, cls)
        except (TypeError, ValueError, KeyError) as e:
            raise ValidationError.for_field("params", str(e))

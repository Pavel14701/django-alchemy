import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from adaptix import Retort

from products.application.types import SORT_FIELDS, SortFields
from products.domain.entities import ProductDM

retort = Retort()


class ValidationError(Exception):
    def __init__(self, field: str, message: str) -> None:
        self.field = field
        self.message = message
        super().__init__(f"{field}: {message}")

    @classmethod
    def for_field(cls, field: str, message: str) -> "ValidationError":
        return cls(field, message)


# --- Query params ---
@dataclass
class ProductQueryParams:
    page: int = 1
    page_size: int = 20
    sort_by: SortFields | None = None
    descending: bool = False

    @classmethod
    def from_raw(cls, raw: Dict[str, Any]) -> "ProductQueryParams":
        val = str(raw.get("descending", "false")).lower()
        if val not in ("true", "false"):
            raise ValidationError.for_field(
                "descending", "Value must be 'true' or 'false'"
            )
        sort_by = raw.get("sort_by")
        if sort_by not in (*SORT_FIELDS, None):
            raise ValidationError.for_field(
                "sort_by", f"Invalid sort field: {sort_by}"
            )
        try:
            page = int(raw.get("page", 1))
            page_size = int(raw.get("page_size", 20))
            if page < 1:
                raise ValidationError.for_field("page", "Must be >= 1")
            if not (1 <= page_size <= 100):
                raise ValidationError.for_field(
                    "page_size", "Must be between 1 and 100"
                )
            normalized = {
                "page": page,
                "page_size": page_size,
                "sort_by": sort_by,
                "descending": val == "true",
            }
            return retort.load(normalized, cls)
        except (TypeError, ValueError) as e:
            raise ValidationError.for_field("params", str(e))


# --- Create product ---
@dataclass
class ProductCreateSchema:
    name: str
    price: Optional[float] = None
    description: Optional[str] = None
    brand: Optional[str] = None
    categories: Optional[List[str]] = None
    in_stock: Optional[int] = None
    media_urls: Optional[List[str]] = None
    currency: str = "USD"

    @classmethod
    def from_raw(cls, raw: Dict[str, Any]) -> "ProductCreateSchema":
        try:
            obj = retort.load(raw, cls)
        except Exception as e:
            raise ValidationError.for_field("body", str(e))

        # Валидация
        if obj.price is not None and obj.price <= 0:
            raise ValidationError.for_field("price", "Must be positive")
        if obj.in_stock is not None and obj.in_stock < 0:
            raise ValidationError.for_field("in_stock", "Must be non-negative")

        # Нормализация
        obj.name = obj.name.strip()
        if obj.brand:
            obj.brand = obj.brand.strip().title()
        if obj.categories:
            obj.categories = [c.strip().lower() for c in obj.categories if c.strip()]
        if obj.media_urls:
            obj.media_urls = [u.strip() for u in obj.media_urls if u.strip()]
        obj.currency = obj.currency.strip().upper()

        return obj

    def to_entity(self) -> ProductDM:
        return ProductDM(
            id=0,
            name=self.name,
            price=self.price,
            description=self.description.strip() if self.description else None,
            brand=self.brand,
            categories=self.categories,
            in_stock=self.in_stock,
            media_urls=self.media_urls,
            currency=self.currency,
        )


# --- Update product ---
@dataclass
class ProductUpdateSchema:
    name: Optional[str] = None
    price: Optional[float] = None
    description: Optional[str] = None
    brand: Optional[str] = None
    categories: Optional[List[str]] = None
    in_stock: Optional[int] = None
    media_urls: Optional[List[str]] = None
    currency: Optional[str] = None

    @classmethod
    def from_raw(cls, raw: Dict[str, Any]) -> "ProductUpdateSchema":
        try:
            obj = retort.load(raw, cls)
        except Exception as e:
            raise ValidationError.for_field("body", str(e))

        if obj.price is not None and obj.price <= 0:
            raise ValidationError.for_field("price", "Must be positive")
        if obj.in_stock is not None and obj.in_stock < 0:
            raise ValidationError.for_field("in_stock", "Must be non-negative")

        # Нормализация
        if obj.name:
            obj.name = obj.name.strip()
        if obj.brand:
            obj.brand = obj.brand.strip().title()
        if obj.categories:
            obj.categories = [c.strip().lower() for c in obj.categories if c.strip()]
        if obj.media_urls:
            obj.media_urls = [u.strip() for u in obj.media_urls if u.strip()]
        if obj.currency:
            obj.currency = obj.currency.strip().upper()

        return obj

    def apply(self, product: ProductDM) -> ProductDM:
        if self.name is not None:
            product.name = self.name
        if self.price is not None:
            product.price = self.price
        if self.description is not None:
            product.description = self.description.strip()
        if self.brand is not None:
            product.brand = self.brand
        if self.categories is not None:
            product.categories = self.categories
        if self.in_stock is not None:
            product.in_stock = self.in_stock
        if self.media_urls is not None:
            product.media_urls = self.media_urls
        if self.currency is not None:
            product.currency = self.currency
        return product


# --- Business operations ---
@dataclass
class DiscountSchema:
    percent: float

    @classmethod
    def from_raw(cls, raw: Dict[str, Any]) -> "DiscountSchema":
        try:
            obj = retort.load(raw, cls)
        except Exception as e:
            raise ValidationError.for_field("percent", str(e))
        if not (0 <= obj.percent <= 100):
            raise ValidationError.for_field("percent", "Must be between 0 and 100")
        return obj


@dataclass
class TaxSchema:
    percent: float

    @classmethod
    def from_raw(cls, raw: Dict[str, Any]) -> "TaxSchema":
        try:
            obj = retort.load(raw, cls)
        except Exception as e:
            raise ValidationError.for_field("percent", str(e))
        if obj.percent < 0:
            raise ValidationError.for_field("percent", "Must be non-negative")
        return obj


@dataclass
class RestockSchema:
    amount: int

    @classmethod
    def from_raw(cls, raw: Dict[str, Any]) -> "RestockSchema":
        try:
            obj = retort.load(raw, cls)
        except Exception as e:
            raise ValidationError.for_field("amount", str(e))
        if obj.amount <= 0:
            raise ValidationError.for_field("amount", "Must be positive")
        return obj


@dataclass
class SellSchema:
    amount: int = 1

    @classmethod
    def from_raw(cls, raw: Dict[str, Any]) -> "SellSchema":
        try:
            obj = retort.load(raw, cls)
        except Exception as e:
            raise ValidationError.for_field("amount", str(e))
        if obj.amount <= 0:
            raise ValidationError.for_field("amount", "Must be positive")
        return obj


@dataclass
class CategorySchema:
    category: str

    @classmethod
    def from_raw(cls, raw: Dict[str, Any]) -> "CategorySchema":
        try:
            obj = retort.load(raw, cls)
        except Exception as e:
            raise ValidationError.for_field("category", str(e))
        if not obj.category.strip():
            raise ValidationError.for_field("category", "Must not be empty")
        normalized = obj.category.strip().lower()
        return cls(category=normalized)


@dataclass
class MediaSchema:
    url: str

    @classmethod
    def from_raw(cls, raw: Dict[str, Any]) -> "MediaSchema":
        try:
            obj = retort.load(raw, cls)
        except Exception as e:
            raise ValidationError.for_field("url", str(e))

        obj.url = obj.url.strip()
        url_regex = re.compile(
            r'^(https?://)'
            r'(([A-Za-z0-9-]+\.)+[A-Za-z]{2,})'
            r'(:\d+)?'
            r'(/[\w\-./?%&=]*)?$'
        )
        if not url_regex.match(obj.url):
            raise ValidationError.for_field("url", f"Invalid URL format: {obj.url}")
        return obj


@dataclass
class BrandSchema:
    brand: str

    @classmethod
    def from_raw(cls, raw: Dict[str, Any]) -> "BrandSchema":
        try:
            obj = retort.load(raw, cls)
        except Exception as e:
            raise ValidationError.for_field("brand", str(e))

        # Проверка на пустую строку
        if not obj.brand.strip():
            raise ValidationError.for_field("brand", "Must not be empty")

        # Нормализация: убираем пробелы и приводим к Title Case
        normalized = obj.brand.strip().title()

        return cls(brand=normalized)

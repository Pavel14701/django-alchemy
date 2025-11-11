from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from adaptix import Retort

from products.application.types import SORT_FIELDS, SortFields
from products.domain.entities import Product

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
        # sourcery skip: raise-from-previous-error
        val = str(raw.get("descending", "false")).lower()
        if val not in ("true", "false"):
            raise ValidationError.for_field(
                "descending", "Value must be 'true' or 'false'"
                )

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
        # sourcery skip: raise-from-previous-error
        try:
            return retort.load(raw, cls)
        except Exception as e:
            raise ValidationError.for_field("body", str(e))

    def to_entity(self) -> "Product":
        return Product(
            id=0,
            name=self.name,
            price=self.price,
            description=self.description,
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
        # sourcery skip: raise-from-previous-error
        try:
            return retort.load(raw, cls)
        except Exception as e:
            raise ValidationError.for_field("body", str(e))

    def apply(self, product: "Product") -> "Product":
        if self.name is not None:
            product.name = self.name
        if self.price is not None:
            product.price = self.price
        if self.description is not None:
            product.description = self.description
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
        # sourcery skip: raise-from-previous-error
        try:
            return retort.load(raw, cls)
        except Exception as e:
            raise ValidationError.for_field("percent", str(e))


@dataclass
class TaxSchema:
    percent: float

    @classmethod
    def from_raw(cls, raw: Dict[str, Any]) -> "TaxSchema":
        # sourcery skip: raise-from-previous-error
        try:
            return retort.load(raw, cls)
        except Exception as e:
            raise ValidationError.for_field("percent", str(e))


@dataclass
class RestockSchema:
    amount: int

    @classmethod
    def from_raw(cls, raw: Dict[str, Any]) -> "RestockSchema":
        # sourcery skip: raise-from-previous-error
        try:
            return retort.load(raw, cls)
        except Exception as e:
            raise ValidationError.for_field("amount", str(e))


@dataclass
class SellSchema:
    amount: int = 1

    @classmethod
    def from_raw(cls, raw: Dict[str, Any]) -> "SellSchema":
        # sourcery skip: raise-from-previous-error
        try:
            return retort.load(raw, cls)
        except Exception as e:
            raise ValidationError.for_field("amount", str(e))


@dataclass
class CategorySchema:
    category: str

    @classmethod
    def from_raw(cls, raw: Dict[str, Any]) -> "CategorySchema":
        # sourcery skip: raise-from-previous-error
        try:
            return retort.load(raw, cls)
        except Exception as e:
            raise ValidationError.for_field("category", str(e))


@dataclass
class MediaSchema:
    url: str

    @classmethod
    def from_raw(cls, raw: Dict[str, Any]) -> "MediaSchema":
        # sourcery skip: raise-from-previous-error
        try:
            return retort.load(raw, cls)
        except Exception as e:
            raise ValidationError.for_field("url", str(e))


@dataclass
class BrandSchema:
    brand: str

    @classmethod
    def from_raw(cls, raw: Dict[str, Any]) -> "BrandSchema":
        # sourcery skip: raise-from-previous-error
        try:
            return retort.load(raw, cls)
        except Exception as e:
            raise ValidationError.for_field("brand", str(e))

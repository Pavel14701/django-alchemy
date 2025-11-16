from typing import Iterable, List

import msgspec

from products.domain.entities import ProductDM


class ProductDTO(msgspec.Struct):
    id: int
    name: str
    price: float | None
    description: str | None = None
    brand: str | None = None
    categories: List[str] | None = None
    in_stock: int | None = None
    media_urls: List[str] | None = None
    currency: str | None = None

    @classmethod
    def from_entity(cls, product: ProductDM) -> "ProductDTO":
        """
        Маппинг из доменной сущности Product в DTO.
        """
        return cls(
            id=product.id,
            name=product.name,
            price=product.price,
            description=product.description,
            brand=product.brand,
            categories=product.categories,
            in_stock=product.in_stock,
            media_urls=product.media_urls,
        )

    @classmethod
    def from_iterable(cls, products: Iterable[ProductDM]) -> list["ProductDTO"]:
        return [cls.from_entity(p) for p in products]

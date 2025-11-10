from typing import List

import msgspec

from products.domain.entities import Product


class ProductDTO(msgspec.Struct):
    id: int
    name: str
    price: float | None
    description: str | None = None
    brand: str | None = None
    categories: List[str] | None = None
    in_stock: int | None = None
    media_urls: List[str] | None = None

    @classmethod
    def from_entity(cls, product: Product) -> "ProductDTO":
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
    def from_list(cls, products: list[Product]) -> list["ProductDTO"]:
        """
        Маппинг списка доменных сущностей в список DTO.
        """
        return [cls.from_entity(p) for p in products]

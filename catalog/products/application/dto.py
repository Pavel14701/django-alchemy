import msgspec

from products.domain.entities import Product


class ProductDTO(msgspec.Struct):
    id: int
    name: str
    price: float

    @classmethod
    def from_entity(cls, product: Product) -> "ProductDTO":
        """
        Маппинг из доменной сущности Product в DTO.
        """
        return cls(id=product.id, name=product.name, price=product.price)

    @classmethod
    def from_list(cls, products: list[Product]) -> list["ProductDTO"]:
        """
        Маппинг списка доменных сущностей в список DTO.
        """
        return [cls.from_entity(p) for p in products]

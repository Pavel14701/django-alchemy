from typing import List, Optional, Protocol

from products.application.types import SortFields

from ..domain.entities import Product


class IProductRepository(Protocol):
    def get_all(
        self,
        offset: int = 0,
        limit: int = 20,
        sort_by: SortFields | None = None,
        descending: bool = False,
    ) -> List[Product]: 
        raise NotImplementedError()

    def count(self) -> int:
        raise NotImplementedError()

    def get_by_id(self, product_id: int) -> Optional[Product]:
        raise NotImplementedError()

    def add(self, product: Product) -> Product:
        raise NotImplementedError()

    def update(self, product: Product) -> Product:
        raise NotImplementedError()

    def delete(self, product_id: int) -> None:
        raise NotImplementedError()

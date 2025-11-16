from typing import List, Optional, Protocol

from products.application.types import SortFields

from ..domain.entities import ProductDM


class ProductRepositoryProtocol(Protocol):
    def get_all(
        self,
        offset: int = 0,
        limit: int = 20,
        sort_by: SortFields | None = None,
        descending: bool = False,
    ) -> List[ProductDM]: 
        raise NotImplementedError()

    def count(self) -> int:
        raise NotImplementedError()

    def get_by_id(self, product_id: int) -> Optional[ProductDM]:
        raise NotImplementedError()

    def add(self, product: ProductDM) -> ProductDM:
        raise NotImplementedError()

    def update(self, product: ProductDM) -> ProductDM:
        raise NotImplementedError()

    def delete(self, product_id: int) -> None:
        raise NotImplementedError()

from typing import List, Protocol

from products.application.types import SortFields

from ..domain.entities import Product


class IProductRepository(Protocol):
    def get_all(
        self,
        offset: int = 0,
        limit: int = 20,
        sort_by: SortFields | None = None,
        descending: bool = False,
    ) -> List[Product]: ...

    def count(self) -> int: ...

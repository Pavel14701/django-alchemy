# products/application/services.py
from typing import List, Tuple

from products.application.types import SortFields

from .dto import ProductDTO
from .interfaces import IProductRepository


class ProductService:
    def __init__(self, repo: IProductRepository) -> None:
        self.repo = repo

    def list_products(
        self,
        page: int = 1,
        page_size: int = 20,
        sort_by: SortFields | None = None,
        descending: bool = False,
    ) -> Tuple[List[ProductDTO], int]:
        offset = (page - 1) * page_size
        products = self.repo.get_all(
            offset=offset,
            limit=page_size,
            sort_by=sort_by,
            descending=descending,
        )
        total = self.repo.count()
        return [
            ProductDTO(id=p.id, name=p.name, price=p.price)
            for p in products
        ], total

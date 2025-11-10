# products/application/interactors.py
from typing import List, Tuple

from .dto import ProductDTO
from .services import ProductService
from .types import SortFields


class ListProductsInteractor:
    def __init__(self, service: ProductService) -> None:
        self.service = service

    def execute(
        self,
        page: int = 1,
        page_size: int = 20,
        sort_by: SortFields | None = None,
        descending: bool = False,
    ) -> Tuple[List[ProductDTO], int]:
        if page < 1:
            page = 1
        if page_size < 1:
            page_size = 20
        if page_size > 100:
            page_size = 100

        return self.service.list_products(
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            descending=descending,
        )

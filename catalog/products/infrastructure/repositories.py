# products/infrastructure/repositories.py
from typing import List

from sqlalchemy.orm import Session

from products.infrastructure.models import ProductModel

from ..application.interfaces import IProductRepository, SortFields
from ..domain.entities import Product


class ProductRepository(IProductRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_all(
        self,
        offset: int = 0,
        limit: int = 20,
        sort_by: SortFields | None = None,
        descending: bool = False,
    ) -> List[Product]:
        query = self.session.query(ProductModel)

        if sort_by is not None:
            column = getattr(ProductModel, sort_by)
            if descending:
                column = column.desc()
            query = query.order_by(column)

        rows = query.offset(offset).limit(limit).all()
        return [Product(id=r.id, name=r.name, price=r.price) for r in rows]

    def count(self) -> int:
        return self.session.query(ProductModel).count()

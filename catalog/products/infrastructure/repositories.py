from typing import List, Optional

from sqlalchemy import desc
from sqlalchemy.orm import Session

from products.infrastructure.models import Price, ProductModel

from ..application.interfaces import IProductRepository, SortFields
from ..domain.entities import Product


class ProductRepository(IProductRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_all(
        self,
        offset: int = 0,
        limit: int = 20,
        sort_by: Optional[SortFields] = None,
        descending: bool = False,
    ) -> List[Product]:
        query = self.session.query(ProductModel)

        if sort_by is not None:
            column = getattr(ProductModel, sort_by)
            if descending:
                column = column.desc()
            query = query.order_by(column)

        rows = query.offset(offset).limit(limit).all()
        return [self._to_entity(r) for r in rows]

    def count(self) -> int:
        return self.session.query(ProductModel).count()

    def get_by_id(self, product_id: int) -> Optional[Product]:
        row = self.session.query(ProductModel).filter_by(id=product_id).first()
        return self._to_entity(row) if row else None

    def add(self, product: Product) -> Product:
        """Добавление нового продукта в БД."""
        model = ProductModel(
            name=product.name,
            description=getattr(product, "description", None),
            is_active=True,
        )
        self.session.add(model)
        self.session.commit()

        # если у продукта есть цена — добавляем запись в Price
        if getattr(product, "price", None) is not None:
            price = Price(
                product_id=model.id,
                price=product.price,
                currency="USD",
            )
            self.session.add(price)
            self.session.commit()

        return self._to_entity(model)

    def _to_entity(self, model: ProductModel) -> Product:
        """Преобразование ORM‑модели в доменную сущность."""
        if model is None:
            return None

        latest_price = (
            self.session.query(Price)
            .filter(Price.product_id == model.id)
            .order_by(desc(Price.valid_from))
            .first()
        )

        return Product(
            id=model.id,
            name=model.name,
            price=latest_price.price if latest_price else None,
        )

from typing import List, Optional

from sqlalchemy import desc
from sqlalchemy.orm import Session

from products.infrastructure.models import Brand, Category, Media, Price, ProductModel

from ..application.interfaces import ProductRepositoryProtocol, SortFields
from ..domain.entities import ProductDM


class ProductRepository(ProductRepositoryProtocol):
    def __init__(self, session: Session) -> None:
        self.session = session

    # --- CREATE ---
    def add(self, product: ProductDM) -> ProductDM:
        model = ProductModel(
            name=product.name,
            description=product.description,
            is_active=True,
        )
        self.session.add(model)
        self.session.commit()

        if product.price is not None:
            self._add_price(model.id, product.price, product.currency)

        if product.brand:
            self._ensure_brand(product, model)

        if product.categories:
            self._ensure_categories(product, model)

        if product.media_urls:
            self._ensure_media(product, model)

        return self._to_entity(model)

    # --- READ ---
    def get_by_id(self, product_id: int) -> Optional[ProductDM]:
        row = self.session.query(ProductModel).filter_by(id=product_id).first()
        return None if row is None else self._to_entity(row)

    def get_all(
        self,
        offset: int = 0,
        limit: int = 20,
        sort_by: Optional[SortFields] = None,
        descending: bool = False,
    ) -> List[ProductDM]:
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

    # --- UPDATE ---
    def update(self, product: ProductDM) -> ProductDM:
        model = self.session.query(ProductModel).filter_by(id=product.id).first()
        if model is None:
            raise ValueError("Продукт не найден")

        model.name = product.name
        model.description = product.description

        if product.price is not None:
            self._add_price(model.id, product.price, product.currency)

        if product.brand:
            self._ensure_brand(product, model)

        if product.categories is not None:
            model.categories.clear()
            self._ensure_categories(product, model)

        if product.media_urls is not None:
            model.media.clear()
            self._ensure_media(product, model)

        self.session.commit()
        return self._to_entity(model)

    # --- DELETE ---
    def delete(self, product_id: int) -> None:
        model = self.session.query(ProductModel).filter_by(id=product_id).first()
        if model is None:
            raise ValueError("Продукт не найден")
        self.session.delete(model)
        self.session.commit()

    # --- Вспомогательные методы ---
    def _add_price(
        self, 
        product_id: int, 
        price_value: float, 
        currency: Optional[str]
    ) -> None:
        currency = currency or "USD"
        price = Price(product_id=product_id, price=price_value, currency=currency)
        self.session.add(price)
        self.session.commit()

    def _ensure_brand(self, product: ProductDM, model: ProductModel) -> None:
        brand = self.session.query(Brand).filter_by(name=product.brand).first()
        if not brand:
            brand = Brand(name=product.brand)
            self.session.add(brand)
            self.session.commit()
        model.brand = brand

    def _ensure_categories(self, product: ProductDM, model: ProductModel) -> None:
        for cat_name in product.categories or []:
            category = self.session.query(Category).filter_by(name=cat_name).first()
            if not category:
                category = Category(name=cat_name)
                self.session.add(category)
                self.session.commit()
            model.categories.append(category)

    def _ensure_media(self, product: ProductDM, model: ProductModel) -> None:
        for url in product.media_urls or []:
            media = Media(product_id=model.id, type="image", url=url)
            self.session.add(media)
        self.session.commit()

    # --- Преобразование ORM -> доменная сущность ---
    def _to_entity(self, model: ProductModel) -> ProductDM:
        latest_price = (
            self.session.query(Price)
            .filter(Price.product_id == model.id)
            .order_by(desc(Price.valid_from))
            .first()
        )

        return ProductDM(
            id=model.id,
            name=model.name,
            price=latest_price.price if latest_price else None,
            description=model.description,
            brand=model.brand.name if model.brand else None,
            categories=[c.name for c in model.categories] if model.categories else [],
            in_stock=model.inventory[0].quantity if model.inventory else None,
            media_urls=[m.url for m in model.media] if model.media else [],
            currency=latest_price.currency if latest_price else "USD",
        )

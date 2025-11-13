from typing import List, Optional, Tuple

from products.application.types import SortFields

from ..domain.entities import Product
from .dto import ProductDTO
from .interfaces import IProductRepository


class ProductService:
    def __init__(self, repo: IProductRepository) -> None:
        self.repo = repo

    # --- CRUD ---
    def create_product(self, product: Product) -> Product:
        return self.repo.add(product)

    def get_product(self, product_id: int) -> Optional[Product]:
        return self.repo.get_by_id(product_id)

    def update_product(self, product: Product) -> Product:
        return self.repo.update(product)

    def delete_product(self, product_id: int) -> None:
        self.repo.delete(product_id)

    # --- LISTING ---
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
        return [ProductDTO.from_entity(p) for p in products], total

    def set_price(self, product: Product, new_price: float) -> Optional[Product]:
        if new_price <= 0:
            return None
        product.price = round(new_price, 2)
        return self.repo.update(product)

    def apply_discount(self, product: Product, percent: float) -> Optional[Product]:
        if product.price is None:
            return None
        product.price = round(product.price * (1 - percent / 100), 2)
        return self.repo.update(product)

    def apply_tax(self, product: Product, percent: float) -> Optional[Product]:
        if product.price is None:
            return None
        product.price = round(product.price * (1 + percent / 100), 2)
        return self.repo.update(product)

    # --- Логика склада ---
    def is_available(self, product: Product) -> bool:
        return (product.in_stock or 0) > 0

    def restock(self, product: Product, amount: int) -> Product:
        product.in_stock = (product.in_stock or 0) + amount
        return self.repo.update(product)

    def sell(self, product: Product, amount: int = 1) -> Product:
        product.in_stock = (product.in_stock or 0) - amount
        return self.repo.update(product)

    def reserve(self, product: Product, amount: int) -> bool:
        current_stock = product.in_stock or 0
        if current_stock >= amount:
            product.in_stock = current_stock - amount
            self.repo.update(product)
            return True
        return False

    def release(self, product: Product, amount: int) -> Product:
        product.in_stock = (product.in_stock or 0) + amount
        return self.repo.update(product)

    def stock_status(self, product: Product) -> str:
        if not product.in_stock or product.in_stock == 0:
            return "нет в наличии"
        return "мало" if product.in_stock < 5 else "в наличии"

    # --- Категории ---
    def add_category(self, product: Product, category: str) -> Product:
        if product.categories is None:
            product.categories = []
        if category not in product.categories:
            product.categories.append(category)
        return self.repo.update(product)

    def remove_category(self, product: Product, category: str) -> Product:
        if product.categories and category in product.categories:
            product.categories.remove(category)
        return self.repo.update(product)

    def clear_categories(self, product: Product) -> Product:
        product.categories = []
        return self.repo.update(product)

    def has_category(self, product: Product, category: str) -> bool:
        return category in (product.categories or [])

    # --- Медиа ---
    def add_media(self, product: Product, url: str) -> Product:
        if product.media_urls is None:
            product.media_urls = []
        if url not in product.media_urls:
            product.media_urls.append(url)
        return self.repo.update(product)

    def clear_media(self, product: Product) -> Product:
        product.media_urls = []
        return self.repo.update(product)

    def get_main_image(self, product: Product) -> Optional[str]:
        return product.media_urls[0] if product.media_urls else None

    # --- Бренд ---
    def change_brand(self, product: Product, new_brand: str) -> Product:
        product.brand = new_brand
        return self.repo.update(product)

    # --- Удобные методы ---
    def short_description(self, product: Product, max_length: int = 50) -> str:
        if not product.description:
            return ""
        return (
            f"{product.description[:max_length]}..."
            if len(product.description) > max_length
            else product.description
        )

    def full_info(self, product: Product) -> str:
        return " ".join([
            f"{product.name}",
            f"({product.brand or 'без бренда'}) —",
            f"{product.price or 'цена не указана'}",
            f"{product.currency}",
        ])

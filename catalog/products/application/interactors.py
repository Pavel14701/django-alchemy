from typing import List, Optional, Tuple

from products.application.dto import ProductDTO
from products.application.services import ProductService
from products.application.types import SortFields
from products.domain.entities import Product


# --- CRUD ---
class CreateProductInteractor:
    def __init__(self, service: ProductService) -> None:
        self.service = service

    def execute(self, product: Product) -> ProductDTO:
        created = self.service.create_product(product)
        return ProductDTO.from_entity(created)


class GetProductInteractor:
    def __init__(self, service: ProductService) -> None:
        self.service = service

    def execute(self, product_id: int) -> Optional[ProductDTO]:
        product = self.service.get_product(product_id)
        return ProductDTO.from_entity(product) if product else None


class UpdateProductInteractor:
    def __init__(self, service: ProductService) -> None:
        self.service = service

    def execute(self, product: Product) -> ProductDTO:
        updated = self.service.update_product(product)
        return ProductDTO.from_entity(updated)


class DeleteProductInteractor:
    def __init__(self, service: ProductService) -> None:
        self.service = service

    def execute(self, product_id: int) -> None:
        self.service.delete_product(product_id)


# --- LISTING ---
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
        page = max(page, 1)
        if page_size < 1:
            page_size = 20
        page_size = min(page_size, 100)
        return self.service.list_products(
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            descending=descending,
        )


# --- Логика цен ---
class SetPriceInteractor:
    def __init__(self, service: ProductService) -> None:
        self.service = service

    def execute(self, product: Product, new_price: float) -> ProductDTO:
        updated = self.service.set_price(product, new_price)
        return ProductDTO.from_entity(updated)


class ApplyDiscountInteractor:
    def __init__(self, service: ProductService) -> None:
        self.service = service

    def execute(self, product_dto: ProductDTO, percent: float) -> ProductDTO:
        from products.domain.entities import Product
        product = Product(
            id=product_dto.id,
            name=product_dto.name,
            price=product_dto.price,
            description=product_dto.description,
            brand=product_dto.brand,
            categories=product_dto.categories,
            in_stock=product_dto.in_stock,
            media_urls=product_dto.media_urls,
        )
        updated = self.service.apply_discount(product, percent)
        return ProductDTO.from_entity(updated)


class ApplyTaxInteractor:
    def __init__(self, service: ProductService) -> None:
        self.service = service

    def execute(self, product: Product, percent: float) -> ProductDTO:
        updated = self.service.apply_tax(product, percent)
        return ProductDTO.from_entity(updated)


# --- Логика склада ---
class RestockProductInteractor:
    def __init__(self, service: ProductService) -> None:
        self.service = service

    def execute(self, product: Product, amount: int) -> ProductDTO:
        updated = self.service.restock(product, amount)
        return ProductDTO.from_entity(updated)


class SellProductInteractor:
    def __init__(self, service: ProductService) -> None:
        self.service = service

    def execute(self, product: Product, amount: int = 1) -> ProductDTO:
        updated = self.service.sell(product, amount)
        return ProductDTO.from_entity(updated)


class ReserveProductInteractor:
    def __init__(self, service: ProductService) -> None:
        self.service = service

    def execute(self, product: Product, amount: int) -> bool:
        return self.service.reserve(product, amount)


class ReleaseProductInteractor:
    def __init__(self, service: ProductService) -> None:
        self.service = service

    def execute(self, product: Product, amount: int) -> ProductDTO:
        updated = self.service.release(product, amount)
        return ProductDTO.from_entity(updated)


class StockStatusInteractor:
    def __init__(self, service: ProductService) -> None:
        self.service = service

    def execute(self, product: Product) -> str:
        return self.service.stock_status(product)


# --- Категории ---
class AddCategoryInteractor:
    def __init__(self, service: ProductService) -> None:
        self.service = service

    def execute(self, product: Product, category: str) -> ProductDTO:
        updated = self.service.add_category(product, category)
        return ProductDTO.from_entity(updated)


class RemoveCategoryInteractor:
    def __init__(self, service: ProductService) -> None:
        self.service = service

    def execute(self, product: Product, category: str) -> ProductDTO:
        updated = self.service.remove_category(product, category)
        return ProductDTO.from_entity(updated)


class ClearCategoriesInteractor:
    def __init__(self, service: ProductService) -> None:
        self.service = service

    def execute(self, product: Product) -> ProductDTO:
        updated = self.service.clear_categories(product)
        return ProductDTO.from_entity(updated)


class HasCategoryInteractor:
    def __init__(self, service: ProductService) -> None:
        self.service = service

    def execute(self, product: Product, category: str) -> bool:
        return self.service.has_category(product, category)


# --- Медиа ---
class AddMediaInteractor:
    def __init__(self, service: ProductService) -> None:
        self.service = service

    def execute(self, product: Product, url: str) -> ProductDTO:
        updated = self.service.add_media(product, url)
        return ProductDTO.from_entity(updated)


class ClearMediaInteractor:
    def __init__(self, service: ProductService) -> None:
        self.service = service

    def execute(self, product: Product) -> ProductDTO:
        updated = self.service.clear_media(product)
        return ProductDTO.from_entity(updated)


class GetMainImageInteractor:
    def __init__(self, service: ProductService) -> None:
        self.service = service

    def execute(self, product: Product) -> Optional[str]:
        return self.service.get_main_image(product)


# --- Бренд ---
class ChangeBrandInteractor:
    def __init__(self, service: ProductService) -> None:
        self.service = service

    def execute(self, product: Product, new_brand: str) -> ProductDTO:
        updated = self.service.change_brand(product, new_brand)
        return ProductDTO.from_entity(updated)


# --- Удобные методы ---
class ShortDescriptionInteractor:
    def __init__(self, service: ProductService) -> None:
        self.service = service

    def execute(self, product: Product, max_length: int = 50) -> str:
        return self.service.short_description(product, max_length)


class FullInfoInteractor:
    def __init__(self, service: ProductService) -> None:
        self.service = service

    def execute(self, product: Product) -> str:
        return self.service.full_info(product)

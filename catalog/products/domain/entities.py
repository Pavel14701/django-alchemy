from dataclasses import dataclass
from typing import List


@dataclass
class Product:
    id: int
    name: str
    price: float | None = None
    description: str | None = None
    brand: str | None = None
    categories: List[str] | None = None
    in_stock: int | None = None
    media_urls: List[str] | None = None

    def apply_discount(self, percent: float) -> None:
        """Пример доменной логики: применить скидку."""
        if percent < 0 or percent > 100:
            raise ValueError("Процент скидки должен быть от 0 до 100")
        if self.price is not None:
            self.price = self.price * (1 - percent / 100)

    def is_available(self) -> bool:
        """Проверка наличия товара на складе."""
        return (self.in_stock or 0) > 0

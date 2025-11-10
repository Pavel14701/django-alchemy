from dataclasses import dataclass


@dataclass
class Product:
    id: int
    name: str
    price: float

    def apply_discount(self, percent: float) -> None:
        """Пример доменной логики: применить скидку."""
        if percent < 0 or percent > 100:
            raise ValueError("Процент скидки должен быть от 0 до 100")
        self.price = self.price * (1 - percent / 100)

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Product:
    id: int
    name: str
    price: Optional[float] = None
    description: Optional[str] = None
    brand: Optional[str] = None
    categories: List[str] | None = None
    in_stock: Optional[int] = None
    media_urls: List[str] | None = None
    currency: Optional[str] = "USD"

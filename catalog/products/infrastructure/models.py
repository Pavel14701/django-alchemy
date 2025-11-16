import datetime

from main.infrastructure.db import Base
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Table,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship


# --- Основная сущность ---
class ProductModel(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    brand_id: Mapped[int] = mapped_column(ForeignKey("brands.id"))
    brand = relationship("Brand", back_populates="products")

    categories = relationship(
        "Category", secondary="product_categories", back_populates="products"
    )
    attributes = relationship("ProductAttribute", back_populates="product")
    prices = relationship("Price", back_populates="product")
    inventory = relationship("Inventory", back_populates="product")
    reviews = relationship("Review", back_populates="product")
    variants = relationship("Variant", back_populates="product")
    tags = relationship("Tag", secondary="product_tags", back_populates="products")
    media = relationship("Media", back_populates="product")


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)
    parent_category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id"), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    products = relationship(
        "ProductModel", secondary="product_categories", back_populates="categories"
    )


product_categories = Table(
    "product_categories",
    Base.metadata,
    Column("product_id", ForeignKey("products.id"), primary_key=True),
    Column("category_id", ForeignKey("categories.id"), primary_key=True),
)


# --- Бренд ---
class Brand(Base):
    __tablename__ = "brands"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    country: Mapped[str] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    products = relationship("ProductModel", back_populates="brand")


# --- Атрибуты ---
class ProductAttribute(Base):
    __tablename__ = "product_attributes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    key: Mapped[str] = mapped_column(String, nullable=False)
    value: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    product = relationship("ProductModel", back_populates="attributes")


# --- Цена и скидки ---
class Price(Base):
    __tablename__ = "prices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    price: Mapped[float] = mapped_column(Float, nullable=True)
    currency: Mapped[str] = mapped_column(String, default="USD", nullable=True)
    valid_from: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc)
    )
    valid_to: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=True)

    product = relationship("ProductModel", back_populates="prices")


# --- Склад ---
class Inventory(Base):
    __tablename__ = "inventory"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int] = mapped_column(Integer, default=0)
    warehouse_id: Mapped[int] = mapped_column(Integer, nullable=True)

    product = relationship("ProductModel", back_populates="inventory")


# --- Отзывы ---
class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc)
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    product = relationship("ProductModel", back_populates="reviews")
    media = relationship("Media", back_populates="review", cascade="all, delete-orphan")
    user = relationship("User", back_populates="reviews")


# --- Теги ---
class Tag(Base):
    __tablename__ = "tags"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    products = relationship(
        "ProductModel", secondary="product_tags", back_populates="tags"
    )


product_tags = Table(
    "product_tags",
    Base.metadata,
    Column("product_id", ForeignKey("products.id"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id"), primary_key=True),
)


# --- Варианты ---
class Variant(Base):
    __tablename__ = "variants"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    sku: Mapped[str] = mapped_column(String, nullable=False)
    size: Mapped[str] = mapped_column(String, nullable=True)
    color: Mapped[str] = mapped_column(String, nullable=True)

    product = relationship("ProductModel", back_populates="variants")


# --- Абстрактное медиа ---
class Media(Base):
    __tablename__ = "media"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    product_id: Mapped[int | None] = mapped_column(
        ForeignKey("products.id"), nullable=True
    )
    review_id: Mapped[int | None] = mapped_column(
        ForeignKey("reviews.id"), nullable=True
    )

    type: Mapped[str] = mapped_column(String, nullable=False)
    url: Mapped[str] = mapped_column(String, nullable=False)
    storage_provider: Mapped[str] = mapped_column(String, default="s3")
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc)
    )

    product = relationship("ProductModel", back_populates="media")
    review = relationship("Review", back_populates="media")

from typing import Iterable, cast
from uuid import UUID

import main.application.interfaces as interfaces
from config import Config
from dishka import AnyOf, Provider, Scope, from_context, provide
from main.infrastructure.db import new_session_maker
from main.infrastructure.redis import new_redis_client
from main.infrastructure.sessions import (
    GuestSessionBackend,
    RedisSessionBackend,
)
from products.application.interactors import ListProductsInteractor
from products.application.services import ProductService
from products.infrastructure.repositories import (
    IProductRepository,
    ProductRepository,
)
from redis import Redis
from sqlalchemy.orm import Session, sessionmaker
from uuid_extensions import uuid7


class CatalogProvider(Provider):
    config = from_context(provides=Config, scope=Scope.APP)

    @provide(scope=Scope.APP)
    def get_session_maker(self, config: Config) -> sessionmaker[Session]:
        return new_session_maker(config.postgres)

    @provide(scope=Scope.REQUEST)
    def get_session(
        self, session_maker: sessionmaker[Session],
    ) -> Iterable[AnyOf[Session, interfaces.ISession]]:
        with session_maker() as session:
            yield session

    @provide(scope=Scope.APP)
    def get_redis_conn(self, config: Config) -> Redis:
        return new_redis_client(config.redis)

    @provide(scope=Scope.APP)
    def get_uuid_generator(self) -> interfaces.UUIDGenerator:
        return lambda: cast(UUID, uuid7())

    product_repository = provide(
        source=ProductRepository,
        scope=Scope.REQUEST,
        provides=IProductRepository,
    )

    product_service = provide(
        source=ProductService,
        scope=Scope.REQUEST,
    )

    list_products_interactor = provide(
        source=ListProductsInteractor,
        scope=Scope.REQUEST,
    )

    redis_session_backend = provide(
        source=RedisSessionBackend,
        provides=interfaces.IRedisSessionBackend,
        scope=Scope.APP
    )

    guest_session_backend = provide(
        source=GuestSessionBackend,
        provides=interfaces.IGuestSessionBackend,
        scope=Scope.APP
    )
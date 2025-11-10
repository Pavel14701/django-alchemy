from typing import Iterable

import interfaces
from config import Config
from db import new_session_maker
from dishka import AnyOf, Provider, Scope, from_context, provide
from products.application.interactors import ListProductsInteractor
from products.application.services import ProductService
from products.infrastructure.repositories import (
    IProductRepository,
    ProductRepository,
)
from sqlalchemy.orm import Session, sessionmaker


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

__all__ = [
    "DishkaMiddleware",
    "FromDishka",
    "inject",
    "setup_dishka",
]

from collections.abc import Callable
from typing import TYPE_CHECKING, ParamSpec, TypeVar

from dishka import Container, FromDishka
from dishka.integrations.base import (
    is_dishka_injected,
    wrap_injection,
)
from django.conf import settings
from django.contrib.sessions.backends.base import SessionBase
from django.http import HttpRequest

if TYPE_CHECKING:
    class DishkaRequest(HttpRequest):
        container: Container
        session: SessionBase
else:
    DishkaRequest = HttpRequest


T = TypeVar("T")
P = ParamSpec("P")

CONTAINER_NAME = "dishka_container"


def inject(func: Callable[P, T]) -> Callable[P, T]:
    """
    Декоратор для Django view, который автоматически инжектит зависимости.
    """
    if not is_dishka_injected(func):
        return wrap_injection(
            func=func,
            is_async=False,
            container_getter=lambda *args, **kwargs: getattr(settings, CONTAINER_NAME),
            manage_scope=True,
        )
    return func


def setup_dishka(container: Container):
    """
    Сохраняем контейнер в Django settings.
    """
    setattr(settings, CONTAINER_NAME, container)


class DishkaMiddleware:
    """
    Middleware, который кладёт контейнер в request для ручного доступа.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: DishkaRequest):
        request.container = getattr(settings, CONTAINER_NAME)
        return self.get_response(request)

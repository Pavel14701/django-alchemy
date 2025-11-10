__all__ = [
    "DishkaMiddleware",
    "FromDishka",
    "inject",
    "setup_dishka",
]

from collections.abc import Callable
from inspect import signature
from typing import TYPE_CHECKING, Any, ParamSpec, TypeVar, get_type_hints

from dishka import Container, DependencyKey, FromDishka
from dishka.integrations.base import (
    default_parse_dependency,
    is_dishka_injected,
    wrap_injection,
)
from django.conf import settings
from django.http import HttpRequest

if TYPE_CHECKING:
    class DishkaRequest(HttpRequest):
        container: Container
else:
    DishkaRequest = HttpRequest


T = TypeVar("T")
P = ParamSpec("P")

CONTAINER_NAME = "dishka_container"


def _django_depends(dependency: DependencyKey) -> Any:
    """
    В Django нет Depends как в FastAPI, поэтому просто возвращаем Annotated.
    """
    return FromDishka[  # type: ignore[misc]
        dependency.type_hint  # type: ignore[name-defined]
    ]


def _replace_depends(func: Callable[P, T]) -> Callable[P, T]:
    """
    Переписываем сигнатуру функции, заменяя зависимости на FromDishka.
    """
    hints = get_type_hints(func, include_extras=True)
    func_signature = signature(func)

    new_params = []
    for name, param in func_signature.parameters.items():
        hint = hints.get(name, Any)
        dep = default_parse_dependency(param, hint)
        if dep is None:
            new_params.append(param)
            continue
        new_dep = _django_depends(dep)
        hints[name] = new_dep
        new_params.append(param.replace(annotation=new_dep))
    func.__signature__ = func_signature.replace(parameters=new_params)  # type: ignore[attr-defined]
    func.__annotations__ = hints
    return func


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

# products/controllers/views.py
import msgspec
from dishka import FromDishka
from django.http import HttpResponse, JsonResponse
from main.integrations import DishkaRequest, inject

from products.application.interactors import ListProductsInteractor
from products.controllers.schemas import ProductQueryParams, ValidationError


@inject
def products_view(
    request: DishkaRequest,
    interactor: FromDishka[ListProductsInteractor],
) -> HttpResponse:
    try:
        params = ProductQueryParams.from_raw(dict(request.GET))
    except ValidationError as e:
        return JsonResponse(
            {"error": "Invalid parameter", "field": e.field, "message": e.message},
            status=400,
        )

    items, total = interactor.execute(
        page=params.page,
        page_size=params.page_size,
        sort_by=params.sort_by,
        descending=params.descending,
    )

    response = {
        "total": total,
        "page": params.page,
        "page_size": params.page_size,
        "items": items,  # already List[ProductDTO]
    }
    return HttpResponse(msgspec.json.encode(response), content_type="application/json")

import msgspec
from dishka import FromDishka
from django.http import HttpResponse, JsonResponse
from main.integrations import DishkaRequest, inject

from products.application.interactors import (
    ApplyDiscountInteractor,
    CreateProductInteractor,
    DeleteProductInteractor,
    GetProductInteractor,
    ListProductsInteractor,
    RestockProductInteractor,
    SellProductInteractor,
    UpdateProductInteractor,
)
from products.controllers.schemas import (
    ProductCreateSchema,
    ProductQueryParams,
    ProductUpdateSchema,
    ValidationError,
)


# --- LIST PRODUCTS ---
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
        "items": items,
    }
    return HttpResponse(msgspec.json.encode(response), content_type="application/json")


# --- GET PRODUCT BY ID ---
@inject
def product_detail_view(
    request: DishkaRequest,
    interactor: FromDishka[GetProductInteractor],
    product_id: int,
) -> HttpResponse:
    if product := interactor.execute(product_id):
        return HttpResponse(
            msgspec.json.encode(product), 
            content_type="application/json"
        )
    else:
        return JsonResponse({"error": "Product not found"}, status=404)


# --- CREATE PRODUCT ---
@inject
def product_create_view(
    request: DishkaRequest,
    interactor: FromDishka[CreateProductInteractor],
) -> HttpResponse:
    try:
        data = msgspec.json.decode(request.body)
        params = ProductCreateSchema.from_raw(data)
    except ValidationError as e:
        return JsonResponse(
            {"error": "Invalid data", "field": e.field, "message": e.message},
            status=400,
        )

    product = interactor.execute(params.to_entity())
    return HttpResponse(
        msgspec.json.encode(product), 
        content_type="application/json", status=201
    )


# --- UPDATE PRODUCT ---
@inject
def product_update_view(
    request: DishkaRequest,
    interactor: FromDishka[UpdateProductInteractor],
    get_interactor: FromDishka[GetProductInteractor],
    product_id: int,
) -> HttpResponse:
    try:
        data = msgspec.json.decode(request.body)
        params = ProductUpdateSchema.from_raw(data)
    except ValidationError as e:
        return JsonResponse(
            {"error": "Invalid data", "field": e.field, "message": e.message},
            status=400,
        )

    product = get_interactor.service.get_product(product_id)
    if not product:
        return JsonResponse({"error": "Product not found"}, status=404)

    updated = interactor.execute(params.apply(product))
    return HttpResponse(msgspec.json.encode(updated), content_type="application/json")


# --- DELETE PRODUCT ---
@inject
def product_delete_view(
    request: DishkaRequest,
    interactor: FromDishka[DeleteProductInteractor],
    product_id: int,
) -> HttpResponse:
    interactor.execute(product_id)
    return JsonResponse({"status": "deleted"})


# --- APPLY DISCOUNT ---
@inject
def product_discount_view(
    request: DishkaRequest,
    discount_interactor: FromDishka[ApplyDiscountInteractor],
    get_interactor: FromDishka[GetProductInteractor],
    product_id: int,
) -> HttpResponse:
    try:
        data = msgspec.json.decode(request.body)
        percent = data.get("percent", 0)
    except Exception:
        return JsonResponse({"error": "Invalid data"}, status=400)

    product = get_interactor.execute(product_id)
    if not product:
        return JsonResponse({"error": "Product not found"}, status=404)
    updated = discount_interactor.execute(product, percent)
    return HttpResponse(msgspec.json.encode(updated), content_type="application/json")


# --- RESTOCK PRODUCT ---
@inject
def product_restock_view(
    request: DishkaRequest,
    interactor: FromDishka[RestockProductInteractor],
    product_id: int,
) -> HttpResponse:
    try:
        data = msgspec.json.decode(request.body)
        amount = data.get("amount", 0)
    except Exception:
        return JsonResponse({"error": "Invalid data"}, status=400)

    product = interactor.service.get_product(product_id)
    if not product:
        return JsonResponse({"error": "Product not found"}, status=404)

    updated = interactor.execute(product, amount)
    return HttpResponse(msgspec.json.encode(updated), content_type="application/json")


# --- SELL PRODUCT ---
@inject
def product_sell_view(
    request: DishkaRequest,
    interactor: FromDishka[SellProductInteractor],
    product_id: int,
) -> HttpResponse:
    try:
        data = msgspec.json.decode(request.body)
        amount = data.get("amount", 1)
    except Exception:
        return JsonResponse({"error": "Invalid data"}, status=400)

    product = interactor.service.get_product(product_id)
    if not product:
        return JsonResponse({"error": "Product not found"}, status=404)

    updated = interactor.execute(product, amount)
    return HttpResponse(msgspec.json.encode(updated), content_type="application/json")

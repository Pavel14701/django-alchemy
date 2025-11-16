from django.http import HttpRequest, JsonResponse
from django.urls import path
from products.controllers import views as products
from users.controllers import views as views

urlpatterns = [
    path("user/register/", views.user_register_view, name="user_register"),
    path("user/auth/", views.user_auth_view, name="user_auth"),
    path("user/activate/", views.user_activate_view, name="user_activate"),
    path(
        "user/suspend/<str:target_username>/", 
        views.user_suspend_view, 
        name="user_suspend"
    ),
    path(
        "user/unsuspend/<str:target_username>/", 
        views.user_unsuspend_view, 
        name="user_unsuspend"
    ),
    path("user/delete/", views.user_delete_view, name="user_delete"),
    path("user/restore/", views.user_restore_view, name="user_restore"),
    path("user/change-role/", views.user_change_role_view, name="user_change_role"),
    path(
        "user/change-password/", 
        views.user_change_password_view, 
        name="user_change_password"
    ),
    path(
        "user/change-username/", 
        views.user_change_username_view, 
        name="user_change_username"
    ),
    path(
        "user/change-email/<str:user_id>/", 
        views.user_change_email_view, 
        name="user_change_email"
    ),
    path("products/", products.products_view, name="products_list"),
    path(
        "products/<int:product_id>/", 
        products.product_detail_view, 
        name="product_detail"
    ),
    path(
        "products/create/", 
        products.product_create_view, 
        name="product_create"
    ),
    path(
        "products/<int:product_id>/update/", 
        products.product_update_view, 
        name="product_update"
    ),
    path(
        "products/<int:product_id>/delete/", 
        products.product_delete_view, 
        name="product_delete"
    ),
    path(
        "products/<int:product_id>/discount/", 
        products.product_discount_view, 
        name="product_discount"
    ),
    path(
        "products/<int:product_id>/restock/", 
        products.product_restock_view, 
        name="product_restock"
    ),
    path(
        "products/<int:product_id>/sell/", 
        products.product_sell_view, 
        name="product_sell"
    ),
]

ERROR_CODES = {
    400: "Bad Request",
    401: "Unauthorized",
    403: "Forbidden",
    404: "Not Found",
    405: "Method Not Allowed",
    408: "Request Timeout",
    429: "Too Many Requests",
    500: "Internal Server Error",
    502: "Bad Gateway",
    503: "Service Unavailable",
    504: "Gateway Timeout",
}

for code, message in ERROR_CODES.items():
    def view(
        request: HttpRequest,
        exception: Exception | None = None,
        status_code: int = code,
        error_message: str = message,
    ) -> JsonResponse:
        return JsonResponse(
            {
                "status": status_code,
                "error": error_message,
            },
            status=status_code,
        )
    globals()[f"error_{code}"] = view

handler400 = "main.urls.error_400"
handler403 = "main.urls.error_403"
handler404 = "main.urls.error_404"
handler500 = "main.urls.error_500"

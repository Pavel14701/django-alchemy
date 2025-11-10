from django.urls import path
from products.controllers.views import products_view

urlpatterns = [
    path("products/", products_view),
]

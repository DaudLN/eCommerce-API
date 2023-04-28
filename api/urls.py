from django.urls import path, re_path
from . import views

app_name = "api"

urlpatterns = [
    path("products/", views.products_list, name="products"),
    path("products/<int:pk>/", views.product, name="products")
]

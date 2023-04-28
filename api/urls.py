from django.urls import path, re_path
from . import views

app_name = "api"

urlpatterns = [
    path("products/", views.ProductList.as_view(), name="products"),
    path("products/<int:pk>/", views.product, name="product"),
    path("collections/", views.collections, name="collections"),
    path("collections/<int:pk>/", views.collection, name="collection"),
]

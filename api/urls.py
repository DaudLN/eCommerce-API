from django.urls import path, re_path
from . import views

app_name = "api"

urlpatterns = [
    path("products/", views.ProductListCreateAPIView.as_view(), name="products"),
    path("products/<int:pk>/", views.ProductDetail.as_view(), name="product"),
    path("collections/", views.CollectionListCreateAPIView.as_view(),
         name="collections"),
    path("collections/<int:pk>/", views.CollectionDetail.as_view(), name="collection"),
]

from django.urls import path, re_path, include
from rest_framework.routers import SimpleRouter, DefaultRouter
from . import views

app_name = "api"

router = DefaultRouter()
router.register("products", views.ProductViewSet)
router.register("collections", views.CollectionViewSet)

urlpatterns = [
    path("", include(router.urls))
]

# urlpatterns = [
#     path("products/", views.ProductListCreateAPIView.as_view(), name="products"),
#     path("products/<int:pk>/", views.ProductDetail.as_view(), name="product"),
#     path("collections/", views.CollectionListCreateAPIView.as_view(),
#          name="collections"),
#     path("collections/<int:pk>/",
#          views.CollectionDetail.as_view(), name="collection"),
# ]

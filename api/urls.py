from django.urls import path, re_path, include
from rest_framework.routers import SimpleRouter, DefaultRouter
from rest_framework_nested import routers
from . import views

app_name = "api"

router = routers.DefaultRouter()
router.register("products", views.ProductViewSet, basename="products")
router.register("collections", views.CollectionViewSet)

products_router = routers.NestedSimpleRouter(
    router, 'products', lookup='product')
products_router.register('reviews', views.ReviewViewSet,
                         basename='product-reviews')

urlpatterns = [
    path("", include(router.urls)),
    path("", include(products_router.urls))
]

# urlpatterns = [
#     path("products/", views.ProductListCreateAPIView.as_view(), name="products"),
#     path("products/<int:pk>/", views.ProductDetail.as_view(), name="product"),
#     path("collections/", views.CollectionListCreateAPIView.as_view(),
#          name="collections"),
#     path("collections/<int:pk>/",
#          views.CollectionDetail.as_view(), name="collection"),
# ]

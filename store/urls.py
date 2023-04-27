from django.urls import path, re_path
from .views import home, product, product_that_has_been_ordered

app_name = "store"

urlpatterns = [
    path("", home, name="home"),
    path("<int:pk>/", product, name="product"),
    path("ordered/", product_that_has_been_ordered, name="ordered-product")
]

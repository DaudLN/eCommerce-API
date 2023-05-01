from django.urls import path, re_path

from . import views

app_name = "store"

urlpatterns = [
    path("", views.home, name="home"),
    path("<int:pk>/", views.product, name="product"),
    path("ordered/", views.product_that_has_been_ordered, name="ordered-product"),
    path("select-related/", views.select_related,
         name="select-related"),
    path("orders/", views.last_five_orders_with_their_customer,
         name="orders"),
    path("stats/", views.statistics,
         name="stats")
]

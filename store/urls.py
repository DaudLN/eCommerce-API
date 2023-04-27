from django.urls import path, re_path
from .views import home, product

app_name = "store"

urlpatterns = [
    path("", home, name="home"),
    path("<int:pk>/", product, name="product")
]

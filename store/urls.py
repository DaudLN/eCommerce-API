from django.urls import path, re_path
from .views import home

app_name = "store"

urlpatterns = [
    path("", home, name="home")
]
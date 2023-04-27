from django.http import HttpResponse
from django.shortcuts import render
from django.utils.translation import gettext as _
from .models import Product
# Create your views here.


def home(request):
    query_set = Product.objects.all()

    message = _("Hoy es 26 de noviembre.")
    # return HttpResponse(message)
    return render(request, "store/index.html",
                  {"name": "Daud Linus Namayala", "message": message,
                      "products": query_set.values()}
                  )


def product(request, pk):
    product = Product.objects.get(pk=pk)
    return render(request, "store/product.html", {"product": product})

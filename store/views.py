from django.db.models import Q, F
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.translation import gettext as _
from .models import Product, OrderItem
# Create your views here.


def home(request):
    query_set = Product.objects.filter(inventory=F('collection__id'))

    message = _("Hoy es 26 de noviembre.")
    # return HttpResponse(message)
    return render(request, "store/index.html",
                  {"name": "Daud Linus Namayala", "message": message,
                      "products": query_set.values()}
                  )


def product(request, pk):
    product = Product.objects.get(pk=pk)
    return render(request, "store/product.html", {"product": product})


def product_that_has_been_ordered(request):
    ordered_qs = OrderItem.objects.values('product__id').distinct()
    products_ordered_qs = Product.objects.filter(
        id__in=[ordered_qs]).order_by("title")
    return render(request, "store/product-ordered.html",
                  {"product_ordered": products_ordered_qs},
                  {"total": products_ordered_qs.count()})

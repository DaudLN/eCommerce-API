from django.db.models import Q, F
from django.db.models.aggregates import Avg, Count, Sum, Max, Min
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.translation import gettext as _
from .models import Product, OrderItem, Order
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


def select_related(request):
    product_qs = Product.objects.prefetch_related(
        "promossions").select_related("collection").all()
    return render(request, "store/select-related.html",
                  {"products": product_qs})


def last_five_orders_with_their_customer(request):
    query_set = Order.objects.select_related("customer")\
        .prefetch_related("orderitem_set__product")\
        .order_by("-placed_at")[:5]
    return render(request, "store/orders.html",
                  {"orders": query_set})


def statistics(request):
    count = Product.objects.aggregate(count=Count("id"))
    max_price = Product.objects.aggregate(max_price=Max("unit_price"))
    min_price = Product.objects.aggregate(min_price=Min("unit_price"))
    total_price = Product.objects.aggregate(total_price=Sum("unit_price"))
    avg_price = Product.objects.aggregate(avg_price=Avg("unit_price"))

    stats = {"count": count, "max_price": max_price,
             "min_price": min_price, "total_price": total_price,
             "avg_price": avg_price}
    return render(request, "store/stats.html",
                  {"stats": stats})

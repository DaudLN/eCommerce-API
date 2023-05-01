from django.contrib import admin, messages
from django.db.models import Count, QuerySet
from django.urls import reverse
from django.utils.html import format_html, urlencode

from . import models

# Register your models here.

# Inlines


class OrderItemInline(admin.TabularInline):
    '''Tabular Inline View for OrderItem'''
    autocomplete_fields = ["product"]
    model = models.OrderItem
    min_num = 1
    max_num = 20
    extra = 0
    # raw_id_fields = ("orderitem_id",)


class InventoryFilter(admin.SimpleListFilter):
    title = 'Inventory'
    parameter_name = 'inventory'

    def lookups(self, request, model_admin):
        return [
            ("<10", "Low"), (">10", "High"),
        ]

    def queryset(self, request, queryset: QuerySet):
        if self.value() == "<10":
            return queryset.filter(inventory__lt=10)
        return queryset.filter(inventory__gt=10)


@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    '''Admin View for Customer'''
    list_display = ["first_name", 'last_name', 'membership', "orders_count"]
    list_editable = ['membership']
    list_filter = ['membership']
    list_per_page = 10
    list_select_related = ['user']
    autocomplete_fields = ['user']
    ordering = ['user__first_name', 'user__last_name']
    search_fields = ["first_name__icontains"]

    @admin.display(ordering="orders_count",)
    def orders_count(self, customer: models.Customer):
        customer_url = reverse("admin:store_order_changelist")+"?" + urlencode(
            {"customer__id": str(customer.id)}
        )
        return format_html(f"<a href='{customer_url}'>{customer.orders_count}</a>")

    def get_queryset(self, request):
        query_set = super().get_queryset(
            request).annotate(orders_count=Count("orders"))
        return query_set


@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    '''Admin View for Collection'''

    list_display = ['title', "products_count"]
    search_fields = ['title']
    autocomplete_fields = ["featured_product"]

    @admin.display(ordering='products_count')
    def products_count(self, collection: models.Collection):
        collection_url = reverse("admin:store_product_changelist")+"?" + urlencode(
            {"collection__id": str(collection.id)}
        )
        return format_html(f"<a href='{collection_url}'>{collection.products_count}</a>")

    def get_queryset(self, request) -> QuerySet:
        queryset = super().get_queryset(request).annotate(
            products_count=Count("products"))
        return queryset


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):

    @admin.action(description="Clear inventory")
    def clear_inventory(self, request, query_set: QuerySet):
        updated_count = query_set.update(inventory=0)
        self.message_user(
            request, f"{updlated_count} products were successfull updated",
            messages.INFO
        )

    '''Admin View for '''
    actions = ['clear_inventory']
    autocomplete_fields = ['collection', ]
    list_display = ["title", 'unit_price',
                    'collection_title', 'inventory_status']
    list_editable = ['unit_price']
    list_filter = ['collection', InventoryFilter]
    list_per_page = 10
    list_select_related = ['collection']
    search_fields = ["title", 'slug']
    prepopulated_fields = {
        'slug': ("title",),
    }

    def collection_title(self, product: models.Product):
        return product.collection.title

    @admin.display(ordering='inventory', description="Inventory status")
    def inventory_status(self, product: models.Product):
        if product.inventory < 10:
            return "Low"
        return "OK"


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    autocomplete_fields = ['customer']
    list_select_related = ['customer']
    list_display = ["id", "placed_at", "payment_status", "customer"]
    list_filter = ["payment_status"]
    inlines = [OrderItemInline]

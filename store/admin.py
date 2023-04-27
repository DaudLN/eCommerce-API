from django.contrib import admin
from . import models
# Register your models here.


@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    '''Admin View for Customer'''
    list_display = ["first_name", 'last_name', 'membership']
    search_fields = ["first_name"]
    list_editable = ['membership']
    list_per_page = 10
    sortable_by = ['first_name']
    list_filter = ['membership',]


@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    '''Admin View for Collection'''

    list_display = ['title']
    search_fields = ['title']


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    '''Admin View for '''
    list_display = ["title", 'unit_price', 'collection', 'inventory']
    search_fields = ["title"]
    list_editable = ['unit_price']
    list_per_page = 10
    sortable_by = ['collection']
    list_filter = ['collection',]

from decimal import Decimal
from rest_framework import serializers
from store import models as store


class CollectionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField(max_length=255)


class ProductSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField(max_length=255)
    unit_price = serializers.DecimalField(6, 2)

    price_with_tax = serializers.SerializerMethodField(
        method_name="calculate_tax")
    collection = CollectionSerializer()

    def calculate_tax(self, product: store.Product):
        return product.unit_price*Decimal(1.1)

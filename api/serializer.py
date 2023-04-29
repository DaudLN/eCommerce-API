from decimal import Decimal
from rest_framework import serializers
from store.models import Product, Collection, Order, Review


# class CollectionSerializer(serializers.Serializer):
#     id = serializers.IntegerField()
#     title = serializers.CharField(max_length=255)


# class ProductSerializer(serializers.Serializer):
#     id = serializers.IntegerField()
#     title = serializers.CharField(max_length=255)
#     unit_price = serializers.DecimalField(6, 2)

#     price_with_tax = serializers.SerializerMethodField(
#         method_name="calculate_tax")
#     collection = CollectionSerializer()

#     def calculate_tax(self, product: store.Product):
#         return product.unit_price*Decimal(1.1)


# Model serializers

class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ['id', 'title', 'products_count']
    products_count = serializers.IntegerField(read_only=True)


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'slug', 'description', 'inventory',
                  'unit_price', 'price_with_tax', 'collection', "orders_count", 'reviews_count']
    collection = serializers.PrimaryKeyRelatedField(
        queryset=Collection.objects.all()
    )
    orders_count = serializers.IntegerField(read_only=True)
    reviews_count = serializers.IntegerField(read_only=True)
    # collection = serializers.HyperlinkedRelatedField(
    #     queryset=Collection.objects.all(),
    #     view_name="api:collection"
    # )
    price_with_tax = serializers.SerializerMethodField(
        method_name="calculate_tax")

    def calculate_tax(self, product: Product):
        return product.unit_price*Decimal(1.1)


class CollectionSerialize(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ['id', 'title', 'products_count']
    products_count = serializers.IntegerField()

    # def number_products(self, collection: Collection):
    #     return collection.featured_product.objects.all().count()


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'name', 'description']

    def create(self, validated_data):
        product_id = self.context['product_id']
        return Review.objects.create(product_id=product_id, **validated_data)

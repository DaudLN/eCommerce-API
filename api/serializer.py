from decimal import Decimal
from rest_framework import serializers
from store.models import Product, Collection, Order, Review, Cart, CartItem

# Model serializers


class CollectionSerializer(serializers.ModelSerializer):
    products_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Collection
        fields = ['id', 'title', 'products_count']


class ProductSerializer(serializers.ModelSerializer):
    orders_count = serializers.IntegerField(read_only=True)
    reviews_count = serializers.IntegerField(read_only=True)
    price_with_tax = serializers.SerializerMethodField(
        method_name="calculate_tax")

    class Meta:
        model = Product
        fields = ['id', 'title', 'slug', 'description', 'inventory',
                  'unit_price', 'price_with_tax', 'collection', "orders_count", 'reviews_count']
    collection = serializers.PrimaryKeyRelatedField(
        queryset=Collection.objects.all()
    )

    def calculate_tax(self, product: Product):
        return product.unit_price*Decimal(1.1)


class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'unit_price']


class CollectionSerialize(serializers.ModelSerializer):
    products_count = serializers.IntegerField()

    class Meta:
        model = Collection
        fields = ['id', 'title', 'products_count']


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'name', 'description']

    def create(self, validated_data):
        product_id = self.context['product_id']
        return Review.objects.create(product_id=product_id, **validated_data)


class CartItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()
    total_price = serializers.SerializerMethodField(
        method_name='calculate_total_price', read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'total_price']

    def calculate_total_price(self, cart_item: CartItem):
        return cart_item.product.unit_price*cart_item.quantity


class CartSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    items = CartItemSerializer(many=True, read_only=True)
    items_count = serializers.IntegerField(read_only=True)
    total_price = serializers.SerializerMethodField(
        "calculate_total_price", read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'items_count', 'items', 'total_price']

    def calculate_total_price(self, cart: Cart):
        return sum([item.quantity*item.product.unit_price for item in cart.items.all()])


class AddCartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()

    class Meta:
        model = CartItem
        fields = ['id', 'product_id', 'quantity']

    def validate_product_id(self, product_id):
        if not Product.objects.filter(pk=product_id).exists():
            raise serializers.ValidationError(
                f"No product with an ID of {product_id}")
        return product_id

    def save(self, **kwargs):
        cart_id = self.context['cart_id']
        product_id = self.validated_data['product_id']
        quantity = self.validated_data['quantity']

        try:  # Update
            cart_item = CartItem.objects.get(
                cart_id=cart_id, product_id=product_id)
            cart_item.quantity += quantity
            cart_item.save()
            self.instance = cart_item
        except CartItem.DoesNotExist:  # Create new cart item
            self.instance = CartItem.objects.create(
                cart_id=cart_id, **self.validated_data)
        return self.instance

class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity']
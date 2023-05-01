from decimal import Decimal

from rest_framework import serializers

from store.models import (Cart, CartItem, Collection, Customer, Order,
                          OrderItem, Product, Review)

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
    # collection = CollectionSerializer()

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


class CustomerSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Customer
        fields = ['id', 'user_id', 'phone', 'birth_date', 'membership']


class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['payment_status']


class OrderItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'unit_price']


class OrderSerializer(serializers.ModelSerializer):
    customer_id = serializers.IntegerField(read_only=True)
    items = OrderItemSerializer(many=True)
    items_count = serializers.IntegerField(read_only=True)
    total_price = serializers.SerializerMethodField(
        method_name='calculate_total_price')

    class Meta:
        model = Order
        fields = ['id', 'customer_id', 'placed_at',
                  'payment_status', 'items', 'items_count', 'total_price']

    def calculate_total_price(self, order: Order):
        return sum([item.unit_price*item.quantity for item in order.items.all()])


class CompleteOrderSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer()
    items = OrderItemSerializer(many=True)
    items_count = serializers.IntegerField(read_only=True)
    total_price = serializers.SerializerMethodField(
        method_name='calculate_total_price')

    class Meta:
        model = Order
        fields = ['id', 'customer', 'placed_at', 'payment_status',
                  'items', 'items_count', 'total_price']

    def calculate_total_price(self, order: Order):
        return sum([item.unit_price*item.quantity for item in order.items.all()])

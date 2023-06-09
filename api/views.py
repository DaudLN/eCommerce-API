from django.db.models import Count
from django.shortcuts import get_object_or_404
from django_filters.rest_framework.backends import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action, api_view
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import (ListCreateAPIView,
                                     RetrieveUpdateDestroyAPIView)
from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin,
                                   RetrieveModelMixin)

from rest_framework.permissions import (
    IsAdminUser, IsAuthenticated)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from store.models import (Cart, CartItem, Collection, Customer, Order,
                          OrderItem, Product, Review)

from .filters import ProductFilter
from .pagination import DefaultPagination
from .permissions import (IsAdminOrReadOnly,
                          ViewCustomerHistoryPermissions)
from .serializers import (AddCartItemSerializer, CartItemSerializer,
                          CartSerializer, CollectionSerializer,
                          CustomerSerializer, CompleteOrderSerializer,
                          OrderSerializer, ProductSerializer,
                          ReviewSerializer, UpdateCartItemSerializer)


@api_view(['GET', 'POST'])
def products_list(request):
    if request.method == 'GET':
        products = Product.objects.select_related("collection")\
            .annotate(orders_count=Count("orderitems")).all()
        serializer = ProductSerializer(
            products, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = ProductSerializer(data=request.data)

        # Nice syntax
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_201_CREATED)

        # if serializer.is_valid():
        #     return Response(serializer.validated_data)
        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def product_detail(request, pk):
    query_set = Product.objects.annotate(
        orders_count=Count("orderitems")).all()
    product = get_object_or_404(query_set, pk=pk)
    if request.method == 'GET':
        serializer = ProductSerializer(product)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = ProductSerializer(product, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    elif request.method == "DELETE":
        if product.orderitems.count() > 0:
            return Response(
                {"error": "This product can't be deleted because it has some orders"},
                status=status.HTTP_405_METHOD_NOT_ALLOWED)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
def collections(request):
    query_set = Collection.objects.annotate(
        products_count=Count("products")).all()
    serializer = CollectionSerializer(query_set, many=True)
    return Response({"message": "success", "results": query_set.count(), "data": serializer.data}, status=status.HTTP_200_OK)


@api_view(['GET', 'PUT', 'DELETE'])
def collection(request, pk):
    query_set = Collection.objects.annotate(
        products_count=Count("products")).all()
    collection = get_object_or_404(query_set, pk=pk)
    serializer = CollectionSerializer(collection)
    return Response(serializer.data)


# Class-based view

class ProductList(APIView):
    def get(self, request):
        query_set = Product.objects.select_related("collection")\
            .annotate(orders_count=Count("orderitems")).all()
        serializer = ProductSerializer(
            query_set, many=True, context={"request": request})
        return Response({
            "message": "success",
            "results": query_set.count(),
            "data": serializer.data})

    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "success", "data": serializer.data}, status=status.HTTP_201_CREATED)


# class ProductDetail(APIView):
#     def get(self, request, pk):
#         query_set = Product.objects.select_related("collection")\
#             .annotate(orders_count=Count("orderitems")).all()
#         serializer = ProductSerializer(
#             get_object_or_404(query_set, pk=pk),
#             context={"request": request})
#         return Response({"message": "success", "data": serializer.data})

#     def put(self, request, pk):
#         product = get_object_or_404(Product, pk=pk)
#         serializer = ProductSerializer(instance=product, data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)

#     def delete(self, request, pk):
#         product = get_object_or_404(Product, pk=pk)
#         if product.orderitems.count() > 0:
#             return Response(
#                 {"error": "This product can't be deleted because it has some orders"},
#                 status=status.HTTP_405_METHOD_NOT_ALLOWED)
#         product.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)

# Generic views


class ProductListCreateAPIView(ListCreateAPIView):
    queryset = Product.objects.select_related("collection")\
        .annotate(orders_count=Count("orderitems"), reviews_count=Count("reviews")).all()

    # def get_queryset(self):
    #     return Product.objects.select_related("collection")\
    #         .annotate(orders_count=Count("orderitems"))

    serializer_class = ProductSerializer

    # def get_serializer_class(self):
    #     return ProductSerializer

    def get_serializer_context(self):
        return {"request": self.request}


class ProductDetail(RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.select_related("collection")\
        .annotate(orders_count=Count("orderitems"),
                  reviews_count=Count("reviews")).all()
    serializer_class = ProductSerializer

    def delete(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        if product.orderitems.count() > 0:
            return Response(
                {"error": "This product can't be deleted because it has some orders"},
                status=status.HTTP_405_METHOD_NOT_ALLOWED)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CollectionListCreateAPIView(ListCreateAPIView):
    queryset = Collection.objects.select_related("featured_product")\
        .annotate(products_count=Count("products")).all()
    serializer_class = CollectionSerializer

    def get_serializer_context(self):
        return {"request": self.request}


class CollectionDetail(RetrieveUpdateDestroyAPIView):
    queryset = Collection.objects.select_related("featured_product")\
        .annotate(products_count=Count("products")).all()
    serializer_class = CollectionSerializer

    def delete(self, request, pk):
        collection = get_object_or_404(Collection, pk=pk)
        if collection.products.count() > 0:
            return Response(
                {"error": "This collection can't be deleted because it has some products"},
                status=status.HTTP_405_METHOD_NOT_ALLOWED)
        collection.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# Using viewsets -> ModelViewSet support all operations to endpoint,
# We may use ReadOnlyModelViewSet to limit operations
# Remember: ViewSet has destroy method for delete


class ProductViewSet(ModelViewSet):
    serializer_class = ProductSerializer

    # Filtering collections -> request.quest_params contains all parameter string
    # We may use third part library (django-filter)
    # def get_queryset(self):
    #     collection_id = self.request.query_params.get('collection')
    #     queryset = Product.objects.select_related("collection")\
    #         .annotate(orders_count=Count("orderitems"), reviews_count=Count("reviews")).all()

    #     if collection_id is not None:
    #         queryset = queryset.filter(collection_id=collection_id)
    #     return queryset
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['title', 'collection__title', 'description']
    filterset_fields = ['collection_id']
    ordering_fields = ['unit_price', 'last_update']
    pagination_class = DefaultPagination
    queryset = Product.objects\
        .annotate(orders_count=Count("orderitems"), reviews_count=Count("reviews")).all()
    # queryset = Product.objects.select_related("collection")\
    #     .annotate(orders_count=Count("orderitems"), reviews_count=Count("reviews")).all()
    # serializer_class = ProductSerializer

    def get_serializer_context(self):
        return {"request": self.request}

    def destroy(self, request, *args, **kwargs):
        if OrderItem.objects.filter(product_id=kwargs['pk']).count() > 0:
            return Response(
                {"error": "This product can't be deleted because it has some orders"},
                status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().destroy(request, *args, **kwargs)


class CollectionViewSet(ModelViewSet):
    queryset = Collection.objects.select_related("featured_product")\
        .annotate(products_count=Count("products")).all()
    serializer_class = CollectionSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_serializer_context(self):
        return {"request": self.request}

    def destroy(self, request, *args, **kwargs):
        if Product.objects.filter(collection_id=kwargs['pk']).count() > 0:
            return Response(
                {"error": "This collection can't be deleted because it has some products"},
                status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().destroy(request, *args, **kwargs)


class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        return Review.objects.filter(product_id=self.kwargs['product_pk']).all()

    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    def get_serializer_context(self):
        return {"product_id": self.kwargs['product_pk']}


class CartViewSet(CreateModelMixin,
                  RetrieveModelMixin,
                  DestroyModelMixin,
                  GenericViewSet):
    def get_serializer_class(self):
        return CartSerializer

    def get_queryset(self):  # FIXME to validate the UUID before querying
        queryset = Cart.objects.filter(pk=self.kwargs['pk']).prefetch_related(
            "items__product").annotate(items_count=Count("items")).all()
        return queryset


class CartItemViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            print(self.request.user)
            return AddCartItemSerializer
        elif self.request.method == 'PATCH':
            return UpdateCartItemSerializer
        return CartItemSerializer

    def get_queryset(self):
        return CartItem.objects.select_related("product")\
            .filter(cart_id=self.kwargs['cart_pk']).all()

    def get_serializer_context(self):
        return {"cart_id": self.kwargs['cart_pk']}


class CustomerViewSet(ModelViewSet):
    """Customer registration form. Register a customer by passing user_id, and other customer 
    details such as Birth date, phone number and membership type of a customer
    """
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAdminUser]

    @action(detail=True, permission_classes=[ViewCustomerHistoryPermissions])
    def history(self, request, pk):
        return Response('Ok')

    @action(detail=False, methods=['GET', 'PUT'], permission_classes=[IsAuthenticated])
    def me(self, request):
        (customer, created) = Customer.objects.select_related(
            "user").get_or_create(user_id=request.user.id)
        if request.method == 'GET':
            serializer = CustomerSerializer(customer)
            return Response(serializer.data)
        elif request.method == 'PUT':
            serializer = CustomerSerializer(customer, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)


class OrderViewSet(ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Order.objects.prefetch_related("items", "items__product")\
            .select_related("customer").annotate(items_count=Count("items"))
        if user.is_staff:
            return queryset.all()
        customer_id = Customer.objects.only('id')\
            .filter(user_id=user.id).first()
        return queryset.filter(customer_id=customer_id)

    @action(detail=False, methods=['GET', 'PUT'], permission_classes=[IsAdminUser])
    def complete(self, request):
        queryset = Order.complete.all()
        serializer = CompleteOrderSerializer(queryset, many=True)
        return Response({"total": len(serializer.data), "data": serializer.data})

    @action(detail=False, methods=['get', 'put'], permission_classes=[IsAdminUser])
    def fail(self, request):
        queryset = Order.fail.all()
        serializer = OrderSerializer(queryset, many=True)
        return Response({"total": len(serializer.data), "data": serializer.data})

    @action(detail=False, methods=['get', 'put'], permission_classes=[IsAdminUser])
    def pending(self, request):
        queryset = Order.pending.all()
        serializer = OrderSerializer(queryset, many=True)
        return Response({"total": len(serializer.data), "data": serializer.data})

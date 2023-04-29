from django.db.models import Count
from django.shortcuts import render, get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from store.models import Product, Collection, OrderItem
from .serializer import ProductSerializer, CollectionSerialize, CollectionSerializer
# Create your views here.


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
    serializer = CollectionSerialize(query_set, many=True)
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
        .annotate(orders_count=Count("orderitems")).all()

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
        .annotate(orders_count=Count("orderitems")).all()
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
    queryset = Product.objects.select_related("collection")\
        .annotate(orders_count=Count("orderitems")).all()
    serializer_class = ProductSerializer

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

    def get_serializer_context(self):
        return {"request": self.request}

    def destroy(self, request, *args, **kwargs):
        if Product.objects.filter(collection_id=kwargs['pk']).count() > 0:
            return Response(
                {"error": "This collection can't be deleted because it has some products"},
                status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().destroy(request, *args, **kwargs)

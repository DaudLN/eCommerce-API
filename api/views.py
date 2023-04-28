from django.db.models import Count
from django.shortcuts import render, get_object_or_404
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework import status
from store.models import Product, Collection
from .serializer import ProductSerializer, CollectionSerialize
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
    serializer = CollectionSerialize(collection)
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


class ProductDetail(APIView):
    def get(self, request, pk):
        query_set = Product.objects.select_related("collection").all()
        serializer = ProductSerializer(
            get_object_or_404(query_set, pk=pk),
            context={"request": request})
        return Response(serializer.data)

    def put(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        serializer = ProductSerializer(instance=product, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        if product.orderitems.count() > 0:
            return Response(
                {"error": "This product can't be deleted because it has some orders"},
                status=status.HTTP_405_METHOD_NOT_ALLOWED)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

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
        products = Product.objects.select_related("collection").all()
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
def product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    serializer = ProductSerializer(product)
    return Response(serializer.data)


@api_view(['GET', 'POST'])
def collections(request):
    query_set = Collection.objects.annotate(
        products_count=Count("products")).all()
    serializer = CollectionSerialize(query_set, many=True)
    return Response(serializer.data)


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
        query_set = Product.objects.select_related("collection").all()
        serializer = ProductSerializer(
            query_set, many=True, context={"request": request})
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def get_context_data(self, request):
        context = {"request": request}
        return context

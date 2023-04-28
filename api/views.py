from django.shortcuts import render, get_object_or_404
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.decorators import api_view
from rest_framework import status
from store.models import Product
from .serializer import ProductSerializer
# Create your views here.


@api_view(['GET', 'POST'])
def products_list(request):
    if request.method == 'GET':
        products = Product.objects.select_related("collection").all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = ProductSerializer(data=request.data)

        # Nice syntax
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data)

        # if serializer.is_valid():
        #     return Response(serializer.validated_data)
        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
def product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    serializer = ProductSerializer(product)
    return Response(serializer.data)

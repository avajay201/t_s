from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Category, FoodItem
from .serializers import CategorySerializer, FoodItemSerializer
from utils.helpers import serializer_first_error



class CategoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        categories = Category.objects.filter(seller=request.user.seller)
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        data = request.data.copy()
        data['seller'] = request.user.seller.id
        serializer = CategorySerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        error = serializer_first_error(serializer)
        return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)


class FoodItemView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        items = FoodItem.objects.filter(seller=request.user.seller)
        serializer = FoodItemSerializer(items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        data = request.data.copy()
        data['seller'] = request.user.seller.id
        serializer = FoodItemSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        error = serializer_first_error(serializer)
        return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

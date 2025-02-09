from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Order
from .serializers import OrderSerializer, OrderViewSerializer
from utils.helpers import serializer_first_error



class OrderView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(seller=request.user.seller)
        serializer = OrderViewSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        data = request.data.copy()
        data['seller'] = request.user.seller.id
        for item in data['items']:
            item['seller'] = request.user.seller.id
        serializer = OrderSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            order = Order.objects.filter(id=serializer.data['id'], seller=request.user.seller).first()
            serializer = OrderViewSerializer(order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        error = serializer_first_error(serializer)
        return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)


class OrderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            order = Order.objects.get(id=pk, seller=request.user.seller)
            serializer = OrderSerializer(order)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

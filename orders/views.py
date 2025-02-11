from rest_framework.views import APIView
from datetime import datetime
from rest_framework.permissions import IsAuthenticated
from .models import Order
from .serializers import OrderSerializer, OrderViewSerializer
from rest_framework.response import Response
from utils.helpers import serializer_first_error
from rest_framework import status



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
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)


class OrderFilterAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        specific_date = request.query_params.get('date')

        orders = Order.objects.filter(seller__user=request.user)

        try:
            if specific_date:
                specific_date = datetime.strptime(specific_date.strip(), "%Y-%m-%d").date()
                orders = orders.filter(created_at__date=specific_date)
            elif start_date and end_date:
                start_date = datetime.strptime(start_date.strip(), "%Y-%m-%d").date()
                end_date = datetime.strptime(end_date.strip(), "%Y-%m-%d").date()
                orders = orders.filter(created_at__date__range=[start_date, end_date])
            else:
                return Response({'error': 'Please provide either a specific date or a date range (start_date and end_date).'},
                                status=status.HTTP_400_BAD_REQUEST)

        except:
            return Response({'error': 'Invalid date format. Use YYYY-MM-DD'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = OrderSerializer(orders, many=True)
        return Response({'orders': serializer.data}, status=status.HTTP_200_OK)

from .views import OrderView, OrderDetailView, OrderFilterAPIView
from django.urls import path



urlpatterns = [
    path('orders/', OrderView.as_view(), name='order-list-create'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('filter-orders/', OrderFilterAPIView.as_view(), name='order-filter'),
]

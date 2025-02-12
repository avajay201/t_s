from .views import OrderView, OrderDetailView
from django.urls import path



urlpatterns = [
    path('', OrderView.as_view(), name='order-list-create'),
    path('<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
]

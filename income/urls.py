from .views import IncomeAPIView, IncomeGraphAPIView
from django.urls import path



urlpatterns = [
    path('income/', IncomeAPIView.as_view()),
    path('income-graph/', IncomeGraphAPIView.as_view()),
]

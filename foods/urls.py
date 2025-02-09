from django.urls import path
from .views import CategoryView, FoodItemView

urlpatterns = [
    path('categories/', CategoryView.as_view(), name='category-list-create'),
    path('food-items/', FoodItemView.as_view(), name='food-item-list-create'),
]

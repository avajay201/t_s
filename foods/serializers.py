from rest_framework import serializers
from .models import Category, FoodItem



class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
        extra_kwargs = {'seller': {'write_only': True}}


class FoodItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodItem
        fields = '__all__'
        extra_kwargs = {'seller': {'write_only': True}}

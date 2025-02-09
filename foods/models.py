from accounts.models import Seller
from django.db import models



class Category(models.Model):
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, unique=True)
    image = models.ImageField(upload_to='foods/category', null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name + ' - ' + self.seller.business_name


class FoodItem(models.Model):
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="foods", null=True, blank=True)
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='foods/items', null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.seller.business_name}"

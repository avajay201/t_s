from accounts.models import Seller
from django.db import models
from django.utils.timezone import now
from foods.models import FoodItem
import random
import uuid



class OrderItem(models.Model):
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name="order_items")
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    # price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.quantity} x {self.food_item.name} - {self.seller.business_name}"


class Order(models.Model):
    PAYMENT_METHODS = [
        ('CASH', 'Cash'),
        ('UPI', 'UPI'),
    ]

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('CANCELLED', 'Cancelled'),
    ]

    order_id = models.CharField(max_length=20, unique=True, editable=False)
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name="orders")
    order_number = models.PositiveIntegerField()
    items = models.ManyToManyField(OrderItem, related_name="order")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHODS, default='CASH')
    payment_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('seller', 'order_number')

    def save(self, *args, **kwargs):
        if not self.order_id:
            timestamp = now().strftime("%Y%m%d%H%M%S")
            random_number = str(random.randint(100000, 999999))
            self.order_id = f"{timestamp}{random_number}"
        super().save(*args, **kwargs)
        self.total_price = sum(item.food_item.price * item.quantity for item in self.items.all())
        super().save(update_fields=['total_price'])

    def __str__(self):
        return f"Order {self.order_number} - {self.seller.business_name} - ₹{self.total_price}"

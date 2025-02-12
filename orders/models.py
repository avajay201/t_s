from foods.models import FoodItem
from django.db import models
from django.utils.timezone import now
import random
import razorpay
from accounts.models import Seller
from django.conf import settings
from datetime import timedelta



client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET))


class OrderItem(models.Model):
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name="order_items")
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
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
        ('FAILED', 'Failed'),
    ]

    order_id = models.CharField(max_length=20, unique=True, editable=False)
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name="orders")
    order_number = models.PositiveIntegerField()
    items = models.ManyToManyField(OrderItem, related_name="order")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_code = models.URLField(blank=True, null=True)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHODS, default='CASH')
    order_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    qr_expiry_time = models.DateTimeField(null=True, blank=True)
    # created_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('seller', 'order_number')

    def save(self, *args, **kwargs):
        if not self.order_id:
            timestamp = now().strftime("%Y%m%d%H%M%S")
            random_number = str(random.randint(100000, 999999))
            self.order_id = f"{timestamp}{random_number}"

        super().save(*args, **kwargs)

    def generate_qr_code_url(self):
        """Generate Razorpay QR Code with expiry"""
        expiry_time = now() + timedelta(hours=1)
        print(self.items, 'Price:', self.total_price)
        payload = {
            "type": "upi_qr",
            "name": self.seller.business_name,
            "usage": "single_use",
            "fixed_amount": True,
            "payment_amount": float(self.total_price) * 100,
            "description": f"Payment for Order {self.order_number}",
            "close_by": int(expiry_time.timestamp()),
            "notes": {
                "purpose": "Order Payment"
            }
        }

        try:
            qr_code = client.qrcode.create(payload)
            print('QR Code:', qr_code)
            self.payment_code = qr_code['image_url']
            self.qr_expiry_time = expiry_time
            self.save(update_fields=['payment_code', 'qr_expiry_time'])
        except Exception as e:
            print("Error generating QR Code:", e)
            self.order_status = 'FAILED'
            self.save(update_fields=['order_status'])

    def __str__(self):
        return f"Order {self.order_number} - {self.seller.business_name}"

from django.contrib import admin
from .models import OTP, Seller, Account


admin.site.register(Account)
admin.site.register(OTP)
admin.site.register(Seller)

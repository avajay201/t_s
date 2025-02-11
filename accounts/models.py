from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import User



class OTP(models.Model):
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    otp_sent = models.IntegerField(default=0)
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.otp} for {self.email}'

class Seller(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_pic = models.ImageField(upload_to='sellers/profiles')
    business_name = models.CharField(max_length=250, unique=True)
    mobile_number = models.CharField(max_length=13, unique=True)
    business_address = models.TextField()
    # created_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.business_name} - {self.user.username}'

class Account(models.Model):
    account_type_choices = (
        ('upi', 'UPI'),
        ('bank_account', 'Bank Account'),
    )
    seller = models.OneToOneField(Seller, on_delete=models.CASCADE)
    account_type = models.CharField(max_length=12, choices=account_type_choices)
    upi = models.CharField(max_length=250, unique=True, null=True, blank=True)
    beneficiary_name = models.CharField(max_length=250, null=True, blank=True)
    bank_name = models.CharField(max_length=250, null=True, blank=True)
    ifsc_code = models.CharField(max_length=11, null=True, blank=True)
    account_number = models.CharField(max_length=250,unique=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.seller.user.username} - {self.account_type}'

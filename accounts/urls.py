from .views import RegistrationView, LoginView, AccountView, SendOTPView, VerifyOTPView, PasswordResetView
from django.urls import path



urlpatterns = [
    path('send-verification-otp/', SendOTPView.as_view()),
    path('verify-otp/', VerifyOTPView.as_view()),
    path('register/', RegistrationView.as_view()),
    path('login/', LoginView.as_view()),
    path('reset-password/', PasswordResetView.as_view()),
    path('account/', AccountView.as_view()),
]

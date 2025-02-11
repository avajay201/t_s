from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.utils.timezone import now
from .models import OTP, Seller, User, Account
import random
from rest_framework_simplejwt.tokens import RefreshToken
from django.template.loader import render_to_string
from rest_framework.response import Response
from .serializers import RegistrationSerializer, AccountSerializer
from django.core.mail import send_mail
from utils.helpers import serializer_first_error
from django.conf import settings
from rest_framework import status
from django.utils.html import strip_tags
from datetime import timedelta



class SendOTPView(APIView):
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email address is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            otp_obj, created = OTP.objects.get_or_create(email=email)
            current_time = now()

            if not created and (current_time - otp_obj.created_at) >= timedelta(days=1):
                otp_obj.otp_sent = 0

            if not created and otp_obj.otp_sent >= 5:
                return Response({'error': 'You have exceeded the limit. Please try again after 24 hours.'}, status=status.HTTP_429_TOO_MANY_REQUESTS)

            if not created and otp_obj.created_at > current_time - timedelta(minutes=1):
                return Response({'error': 'OTP already sent. Please wait a minute before requesting again.'}, status=status.HTTP_429_TOO_MANY_REQUESTS)

            otp = str(random.randint(100000, 999999))
            otp_obj.otp = otp
            otp_obj.otp_sent += 1
            html_message = render_to_string('otp_email_template.html', {'otp': otp})
            plain_message = strip_tags(html_message)
            send_mail(
                subject='Your OTP Verification Code',
                message=plain_message,
                from_email=f'Test {settings.EMAIL_HOST_USER}',
                recipient_list=[email],
                html_message=html_message
            )
            otp_obj.save()
            return Response({'message': 'OTP sent successfully. Please check your email.'}, status=status.HTTP_200_OK)
        except Exception as err:
            if created:
                otp_obj.delete()
            print('Error:', err)
            return Response({'error': 'Failed to send OTP.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class VerifyOTPView(APIView):
    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')
        verification_type = request.data.get('type')
        if verification_type and verification_type != 'fp':
            return Response({'error': 'Invalid request.'}, status=status.HTTP_400_BAD_REQUEST)

        if not email or not otp:
            return Response({'error': 'Email and OTP are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            otp_obj = OTP.objects.get(email=email, otp=otp)
            if (now() - otp_obj.updated_at) >= timedelta(minutes=1):
                return Response({'error': 'OTP expired.'}, status=status.HTTP_400_BAD_REQUEST)

            if verification_type and verification_type == 'fp':
                user = User.objects.get(email=email)
                refresh = RefreshToken.for_user(user)
                refresh.payload['exp'] = int((now() + timedelta(minutes=2)).timestamp())
                otp_obj.delete()
                return Response({'message': 'OTP verified.', 'access': str(refresh.access_token)}, status=status.HTTP_200_OK)

            otp_obj.verified = True
            otp_obj.save()
            return Response({'message': 'OTP verified.'}, status=status.HTTP_200_OK)
        except OTP.DoesNotExist:
            return Response({'error': 'Invalid OTP.'}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'error': 'Something went wrong.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class RegistrationView(APIView):
    def post(self, request):
        try:
            serializer = RegistrationSerializer(data=request.data)
            if serializer.is_valid():
                user_otp = OTP.objects.get(email=request.data['email'])
                if not user_otp.verified:
                    return Response({'error': 'Email not verified.'}, status=status.HTTP_400_BAD_REQUEST)

                seller = serializer.save()
                user = seller.user

                refresh = RefreshToken.for_user(user)
                data = serializer.data
                data['access'] = str(refresh.access_token)
                user_otp.delete()
                html_message = render_to_string('registration_successful.html', {'user_name': user.username})
                plain_message = strip_tags(html_message)
                send_mail(
                    subject='Registeration Successful.',
                    message=plain_message,
                    from_email=f'Test {settings.EMAIL_HOST_USER}',
                    recipient_list=[user.email],
                    html_message=html_message
                )
                return Response(data, status=status.HTTP_201_CREATED)

            error = serializer_first_error(serializer)
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)
        except OTP.DoesNotExist:
            return Response({'error': 'Email not verified.'}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'error': 'Something went wrong.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LoginView(APIView):
    def post(self, request):
        identifier = request.data.get('identifier')
        password = request.data.get('password')

        if not identifier or not password:
            return Response({'error': 'Both identifier and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=identifier)
        except User.DoesNotExist:
            user = User.objects.filter(username=identifier).first()

        if not user:
            return Response({'error': 'Invalid email/username or password.'}, status=status.HTTP_401_UNAUTHORIZED)

        authenticated_user = authenticate(username=user.username, password=password)

        if not authenticated_user:
            return Response({'error': 'Invalid email/username or password.'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            seller = Seller.objects.get(user=user)
        except Seller.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        refresh = RefreshToken.for_user(user)

        serializer = RegistrationSerializer(seller)

        data = serializer.data
        data['access'] = str(refresh.access_token)

        return Response(data, status=status.HTTP_200_OK)


class AccountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            seller = Seller.objects.get(user=request.user)
            account = Account.objects.get(seller=seller)
            serializer = AccountSerializer(account)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Seller.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Account.DoesNotExist:
            return Response({'error': 'Account details not found for this seller.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as err:
            print('Error:', err)
            return Response({'error': 'Something went wrong'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            seller = Seller.objects.get(user=request.user)
        except Seller.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        data = request.data
        data['User'] = seller.id

        account = Account.objects.get(seller=seller)
        if account:
            return Response({'error': 'Account details already exists for this seller.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = AccountSerializer(data=data)
        try:
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            error = serializer_first_error(serializer)
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as err:
            print('Error:', err)
            return Response({'error': 'Something went wrong'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PasswordResetView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        password = request.data.get('password')
        confirm_password = request.data.get('confirm_password')
        reset_type = request.data.get('type')
        current_password = request.data.get('current_password')

        if not reset_type or reset_type not in ['fp', 'cp']:
            return Response({'error': 'Invalid request.'}, status=status.HTTP_400_BAD_REQUEST)

        if reset_type == 'cp' and not current_password:
            return Response({'error': 'Current password is required.'}, status=status.HTTP_400_BAD_REQUEST)
        elif reset_type == 'cp' and not request.user.check_password(current_password):
            return Response({'error': 'Current password is incorrect.'}, status=status.HTTP_400_BAD_REQUEST)

        if not password or not confirm_password or not reset_type:
            return Response({'error': 'Password, Confirm password are required.'}, status=status.HTTP_400_BAD_REQUEST)
        elif len(password) < 6:
            return Response({'error': 'Password must be at least 6 characters.'}, status=status.HTTP_400_BAD_REQUEST)
        elif password != confirm_password:
            return Response({'error': 'Passwords do not match.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            _ = Seller.objects.get(user=request.user)
            request.user.set_password(password)
            request.user.save()
            refresh = RefreshToken.for_user(request.user)
            if reset_type == 'cp':
                return Response({'message': 'Password changed successfully.', 'access': str(refresh.access_token)}, status=status.HTTP_200_OK)
            return Response({'message': 'Password reset successfully.',}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Seller.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as err:
            print('Error:', err)
            return Response({'error': 'Something went wrong'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

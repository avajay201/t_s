from .models import Seller, User, Account
from rest_framework import serializers



class RegistrationSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True)
    profile_pic = serializers.ImageField()
    business_name = serializers.CharField()
    mobile_number = serializers.CharField()
    business_address = serializers.CharField()

    class Meta:
        model = Seller
        fields = ['first_name', 'last_name', 'username', 'password', 'confirm_password', 'email', 'profile_pic', 'business_name', 'mobile_number', 'business_address']

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({'confirm_password': 'Passwords do not match.'})

        if len(data['username']) < 6:
            raise serializers.ValidationError({'username': 'Username must have at least 6 characters.'})

        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError({'username': 'Username is already taken.'})

        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({'email': 'Email is already registered.'})

        if len(data['first_name']) < 3:
            raise serializers.ValidationError({'first_name': 'First name must have at least 3 characters.'})

        if len(data['last_name']) < 3:
            raise serializers.ValidationError({'last_name': 'Last name must have at least 3 characters.'})

        if len(data['password']) < 6:
            raise serializers.ValidationError({'password': 'Password must be at least 6 characters.'})

        return data

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['first_name'] = instance.user.first_name
        representation['last_name'] = instance.user.last_name
        representation['username'] = instance.user.username
        representation['email'] = instance.user.email
        representation['profile_pic'] = instance.profile_pic.url if instance.profile_pic else None
        return representation

    def create(self, validated_data):
        first_name = validated_data.pop('first_name')
        last_name = validated_data.pop('last_name')
        username = validated_data.pop('username')
        password = validated_data.pop('password')
        validated_data.pop('confirm_password')
        email = validated_data.pop('email')

        user = User.objects.create_user(username=username, password=password, email=email, first_name=first_name, last_name=last_name)
        seller = Seller.objects.create(user=user, **validated_data)

        return seller


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = '__all__'

    def validate(self, data):
        print('Data:', data)
        if data['account_type'] == 'upi':
            upi = data.get('upi')
            if not upi:
                raise serializers.ValidationError({'upi': 'This field is required.'})
        else:
            beneficiary_name = data.get('beneficiary_name')
            bank_name = data.get('bank_name')
            ifsc_code = data.get('ifsc_code')
            account_number = data.get('account_number')
            if not beneficiary_name:
                raise serializers.ValidationError({'beneficiary_name': 'This field is required.'})
            if not bank_name:
                raise serializers.ValidationError({'bank_name': 'This field is required.'})
            if not ifsc_code:
                raise serializers.ValidationError({'ifsc_code': 'This field is required.'})
            if not account_number:
                raise serializers.ValidationError({'account_number': 'This field is required.'})
        return data

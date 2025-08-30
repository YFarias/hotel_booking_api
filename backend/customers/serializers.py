from rest_framework import serializers
from .models import Customer
from users.serializers import UserSerializer
from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()

class CustomerSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Customer
        fields = ['id', 'user', 'preferences']
        read_only_fields = ['id']

class CustomerCreateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    phone = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True, min_length=8)
    preferences = serializers.JSONField(required=False, default=dict)

    class Meta:
        model = Customer
        fields = ['name', 'email', 'phone', 'password', 'preferences']

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        preferences = validated_data.pop('preferences', {})
        with transaction.atomic():
            user = User.objects.create_user(
                name=validated_data['name'],
                email=validated_data['email'],
                phone=validated_data['phone'],
                password=password,
                is_customer=True
            )
            customer = Customer.objects.create(
                user=user,
                preferences=preferences
            )
        return customer

class CustomerUpdateSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(write_only=True)
    customer_id = serializers.IntegerField(read_only=True)
    preferences = serializers.JSONField(required=False)
    name = serializers.CharField(required=False)
    email = serializers.EmailField(required=False, help_text="Email do cliente")
    phone = serializers.CharField(required=False, help_text="Telefone do cliente")

    class Meta:
        model = Customer
        fields = ["user_id", "customer_id", "preferences", "name", "email", "phone"]

    def update(self, instance, validated_data):
        user_id = validated_data.pop('user_id', None)
        customer_id = validated_data.pop('customer_id', None)
        if not user_id:
            raise serializers.ValidationError("User ID is required")
        if not customer_id:
            raise serializers.ValidationError("Customer ID is required")

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found")

        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            raise serializers.ValidationError("Customer not found")

        # Atualiza apenas os campos fornecidos
        for attr in ['name', 'phone', 'email']:
            value = validated_data.get(attr, None)
            if value is not None:
                setattr(user, attr, value)
        user.save()

        if 'preferences' in validated_data:
            customer.preferences = validated_data['preferences']
            customer.save()

        return customer

        
       

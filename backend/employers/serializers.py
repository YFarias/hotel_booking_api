from rest_framework import serializers
from .models import Employer
from users.serializers import UserSerializer
from hotels.serializers import HotelSerializer
from django.contrib.auth import get_user_model
from hotels.models import Hotel
from django.db import transaction

User = get_user_model()

class EmployerSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    hotel = HotelSerializer(read_only=True)
    
    class Meta:
        model = Employer
        fields = ['id', 'user', 'hotel', 'role', 'is_admin_staff']
        read_only_fields = ['id']

class EmployerCreateSerializer(serializers.ModelSerializer):
    hotel_id = serializers.IntegerField(required=True)
    role = serializers.CharField(required=False, max_length=50)
    is_admin_staff = serializers.BooleanField(required=False, default=False)
    name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    phone = serializers.CharField(required=True)
    password = serializers.CharField(required=True, min_length=8)

    class Meta:
        model = Employer
        fields = ['hotel_id', 'role', 'is_admin_staff', 'name', 'email', 'phone', 'password']

    def validate_hotel_id(self, value):
        if not Hotel.objects.filter(id=value).exists():
            raise serializers.ValidationError("Hotel not found")
        return value

    def validate(self, attrs):
        # check if the user is already an employer of this hotel
        email = attrs['email']
        hotel_id = attrs['hotel_id']
        # The field in Employer is likely 'user', not 'user_email'
        if Employer.objects.filter(user__email=email, hotel_id=hotel_id).exists():
            raise serializers.ValidationError("This user is already an employer of this hotel")
        return attrs

    def create(self, validated_data):
        hotel_id = validated_data.pop('hotel_id')
        hotel = Hotel.objects.filter(id=hotel_id).first()
        if not hotel:
            raise serializers.ValidationError("Hotel not found")

        with transaction.atomic():
            user = User.objects.create_user(
                name=validated_data['name'],
                email=validated_data['email'],
                phone=validated_data['phone'],
                password=validated_data['password'],
                is_employer=True
            )

            employer = Employer.objects.create(
                user=user,
                hotel=hotel,
                role=validated_data.get('role', ''),
                is_admin_staff=validated_data.get('is_admin_staff', False)
            )
        return employer

class EmployerUpdateSerializer(serializers.ModelSerializer):
    employer_id = serializers.IntegerField(required=False)
    user_id = serializers.IntegerField(required=False)
    role = serializers.CharField(required=False, max_length=50)
    is_admin_staff = serializers.BooleanField(required=False, default=False)

    class Meta:
        model = Employer
        fields = ['user_id', 'employer_id', 'role', 'is_admin_staff']

    def update(self, instance, validated_data):
        request_user = self.context['request'].user
        user_id = validated_data.get('user_id')
        employer_id = validated_data.get('employer_id')

        # Use instance if employer_id is not provided
        employer = instance
        user = instance.user

        if user_id:
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                raise serializers.ValidationError("User not found")

        if employer_id:
            try:
                employer = Employer.objects.get(id=employer_id)
            except Employer.DoesNotExist:
                raise serializers.ValidationError("Employer not found")

        # Update user fields if present
        if 'name' in validated_data:
            user.name = validated_data['name']
        if 'email' in validated_data:
            user.email = validated_data['email']
        if 'phone' in validated_data:
            user.phone = validated_data['phone']
        user.save()

        # Only allow role/is_admin_staff update if superuser or admin staff
        is_admin = False
        try:
            is_admin = request_user.is_superuser or Employer.objects.get(user_id=request_user.id).is_admin_staff
        except Employer.DoesNotExist:
            is_admin = request_user.is_superuser

        if is_admin:
            if 'role' in validated_data:
                employer.role = validated_data['role']
            if 'is_admin_staff' in validated_data:
                employer.is_admin_staff = validated_data['is_admin_staff']
            employer.save()

        return employer

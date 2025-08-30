from typing import Any, Dict, Optional
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueValidator



User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "name",
            "email",
            "phone",
            "is_customer",
            "is_employer",
            "is_staff",
            "is_superuser",
        ]

        read_only_fields = fields

class UserCreateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        required=True,
        help_text="Full name of the user"
    )
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())],
        help_text="Unique email address"
    )
    password = serializers.CharField(
        required=True,
        write_only=True,
        help_text="Password for the user"
    )
    phone = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Phone number (optional)"
    )

    class Meta:
        model = User
        fields = [
            "name",
            "email",
            "phone",
            "password",
            "is_customer",
            "is_employer",
            "is_staff",
            "is_superuser",
        ]
        extra_kwargs = {
            "is_customer": {"required": False},
            "is_employer": {"required": False},
            "is_staff": {"required": False},
            "is_superuser": {"required": False},
        }

    def create(self, validated_data):
        """
        Create a new user instance using the validated data.
        The password will be properly hashed by the model's create_user method.
        """
        # if user already exists
        if User.objects.filter(email=validated_data["email"]).exists():
            raise ValidationError("User with this email already exists.")
        
        # create user
        return User.objects.create_user(**validated_data)

class UserUpdateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=True)
    name = serializers.CharField(required=False)
    phone = serializers.CharField(required=False)
    password = serializers.CharField(required=False, write_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "name",
            "phone",
            "password",
            "is_customer",
            "is_employer",
            "is_staff",
            "is_superuser",
        ]

    def update(self, instance, validated_data):
        """
        Update a user instance with the provided validated data.
        The user is identified by the 'id' field in validated_data.
        """
        user_id = validated_data.pop("id", None)
        if user_id is None:
            raise ValidationError("User ID is required to update a user.")

        user = User.objects.filter(id=user_id).first()
        if user is None:
            raise ValidationError("User not found.")

        # Update fields if present in validated_data, otherwise keep existing values
        for field in ["name", "phone", "is_customer", "is_employer", "is_staff", "is_superuser"]:
            if field in validated_data:
                setattr(user, field, validated_data[field])

        # Handle password update separately
        password = validated_data.get("password")
        if password:
            user.set_password(password)

        user.save()
        return user

#delete user
class UserDeleteSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)

    class Meta:
        model = User
        fields = ["id"]

    def delete(self, instance):
        """
        Deletes the user instance provided.
        """
        if not isinstance(instance, User):
            raise ValidationError("Invalid user instance provided.")

        user_id = getattr(instance, "id", None)
        if user_id is None:
            raise ValidationError("User ID is required to delete a user.")

        user = User.objects.filter(id=user_id).first()
        if user is None:
            raise ValidationError("User not found.")

        user.delete()
        return user
        
class UserPasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise ValidationError("User with this email does not exist.")
        return value


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        if not email or not password:
            raise ValidationError("Email and password are required.")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise ValidationError("Invalid credentials")

        if not user.check_password(password):
            raise ValidationError("Invalid credentials")

        attrs["user"] = user  # Optionally attach user for downstream use
        return attrs

class UserLogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField(write_only=True)
    access = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        refresh = attrs.get("refresh")
        access = attrs.get("access")

        if not refresh or not access:
            raise ValidationError("Refresh and access tokens are required.")

        return attrs





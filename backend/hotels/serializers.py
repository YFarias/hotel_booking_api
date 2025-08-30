from rest_framework import serializers
from .models import Hotel
from django.db import transaction

class HotelSerializer(serializers.ModelSerializer):
    full_address = serializers.ReadOnlyField()
    
    class Meta:
        model = Hotel
        fields = [
            'id', 'name', 'email', 'phone', 'street', 'number', 
            'complement', 'city', 'state', 'zip_code', 'website', 'full_address'
        ]
        read_only_fields = ['id']

class HotelCreateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True, help_text="Nome do hotel")
    email = serializers.EmailField(required=True, help_text="Email de contato")
    phone = serializers.CharField(required=True, help_text="Telefone de contato")
    street = serializers.CharField(required=True, help_text="Rua")
    number = serializers.CharField(required=True, help_text="Número")
    complement = serializers.CharField(required=False, allow_blank=True, help_text="Complemento")
    city = serializers.CharField(required=True, help_text="Cidade")
    state = serializers.CharField(required=True, help_text="Estado")
    zip_code = serializers.CharField(required=True, help_text="CEP")
    website = serializers.URLField(required=False, allow_blank=True, help_text="Website do hotel")

    class Meta:
        model = Hotel
        fields = [
            'name', 'email', 'phone', 'street', 'number', 
            'complement', 'city', 'state', 'zip_code', 'website'
        ]

    def create(self, validated_data):
        request_user = self.context['request'].user
        if not request_user.is_superuser:
            raise serializers.ValidationError("You are not allowed to create a hotel")

        with transaction.atomic():
            hotel = Hotel.objects.create(
                name=validated_data['name'],
                email=validated_data['email'],
                phone=validated_data['phone'],
                street=validated_data['street'],
                number=validated_data['number'],
                complement=validated_data.get('complement', ''),
                city=validated_data['city'],
                state=validated_data['state'],
                zip_code=validated_data['zip_code'],
                website=validated_data.get('website', '')
            )

        return hotel

class HotelUpdateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    name = serializers.CharField(required=False, help_text="Nome do hotel")
    email = serializers.EmailField(required=False, help_text="Email de contato")
    phone = serializers.CharField(required=False, help_text="Telefone de contato")
    street = serializers.CharField(required=False, help_text="Rua")
    number = serializers.CharField(required=False, help_text="Número")
    complement = serializers.CharField(required=False, allow_blank=True, help_text="Complemento")
    city = serializers.CharField(required=False, help_text="Cidade")
    state = serializers.CharField(required=False, help_text="Estado")
    zip_code = serializers.CharField(required=False, help_text="CEP")
    website = serializers.URLField(required=False, allow_blank=True, help_text="Website do hotel")

    class Meta:
        model = Hotel
        fields = [
            'id', 'name', 'email', 'phone', 'street', 'number', 
            'complement', 'city', 'state', 'zip_code', 'website'
        ]

    def update(self, instance, validated_data):
        request_user = self.context['request'].user
        hotel_id = validated_data.get('id', instance.id)
        try:
            hotel = Hotel.objects.get(id=hotel_id)
        except Hotel.DoesNotExist:
            raise serializers.ValidationError("Hotel not found")
        
        if not request_user.is_superuser:
            raise serializers.ValidationError("You are not allowed to update a hotel")

        with transaction.atomic():
            hotel.name = validated_data.get('name', hotel.name)
            hotel.email = validated_data.get('email', hotel.email)
            hotel.phone = validated_data.get('phone', hotel.phone)
            hotel.street = validated_data.get('street', hotel.street)
            hotel.number = validated_data.get('number', hotel.number)
            hotel.complement = validated_data.get('complement', hotel.complement)
            hotel.city = validated_data.get('city', hotel.city)
            hotel.state = validated_data.get('state', hotel.state)
            hotel.zip_code = validated_data.get('zip_code', hotel.zip_code)
            hotel.website = validated_data.get('website', hotel.website)
            hotel.save()
        return hotel

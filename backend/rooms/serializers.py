from rest_framework import serializers
from .models import Room
from hotels.serializers import HotelSerializer
from hotels.models import Hotel
from employers.models import Employer

class RoomSerializer(serializers.ModelSerializer):
    hotel = HotelSerializer(read_only=True)
    alias = serializers.ReadOnlyField()
    status = serializers.ReadOnlyField()
    
    class Meta:
        model = Room
        fields = [
            'id', 'hotel', 'number', 'complement', 'is_available', 'alias', 'status'
        ]
        read_only_fields = ['id']

class RoomCreateSerializer(serializers.ModelSerializer):
    hotel_id = serializers.IntegerField(required=True)
    employer_id = serializers.IntegerField(required=True)
    number = serializers.IntegerField(required=True)
    complement = serializers.CharField(required=False, allow_blank=True)
    is_available = serializers.BooleanField(required=False, default=True)

    class Meta:
        model = Room
        fields = ['hotel_id', 'employer_id', 'number', 'complement', 'is_available']

    def create(self, validated_data):
        hotel_id = validated_data.pop('hotel_id')
        employer_id = validated_data.pop('employer_id')

        if not Hotel.objects.filter(id=hotel_id).exists():
            raise serializers.ValidationError("Hotel not found")
        
        if not Employer.objects.filter(id=employer_id).exists():
            raise serializers.ValidationError("Employer not found")
        
        hotel = Hotel.objects.get(id=hotel_id)
        employer = Employer.objects.get(id=employer_id)

        if employer.is_admin_staff:
            room = Room.objects.create(
                hotel=hotel,
                **validated_data
            )
        else:
            raise serializers.ValidationError("You are not allowed to create a room")
        
        return room


class RoomUpdateSerializer(serializers.ModelSerializer):
    hotel_id = serializers.IntegerField(required=True)
    employer_id = serializers.IntegerField(required=True)
    room_id = serializers.IntegerField(required=True)
    number = serializers.IntegerField(required=True)
    complement = serializers.CharField(required=False, allow_blank=True)


    class Meta:
        model = Room
        fields = ['hotel_id', 'employer_id', 'room_id', 'number', 'complement', 'is_available']

    def update(self, instance, validated_data):
        hotel_id = validated_data.get('hotel_id')
        employer_id = validated_data.get('employer_id')
        room_id = validated_data.get('room_id')

        if not Hotel.objects.filter(id=hotel_id).exists():
            raise serializers.ValidationError("Hotel not found")
        
        if not Employer.objects.filter(id=employer_id).exists():
            raise serializers.ValidationError("Employer not found")
        
        if not Room.objects.filter(id=room_id).exists():
            raise serializers.ValidationError("Room not found")
        
        hotel = Hotel.objects.get(id=hotel_id)
        employer = Employer.objects.get(id=employer_id)
        room = Room.objects.get(id=room_id)
        
        if employer.is_admin_staff:
            room.hotel = hotel
            room.number = validated_data.get('number', room.number)
            room.complement = validated_data.get('complement', room.complement)
            room.is_available = validated_data.get('is_available', room.is_available)
            room.save()
            return room
        else:
            raise serializers.ValidationError("You are not allowed to update this room")
       

class RoomDeleteSerializer(serializers.ModelSerializer):
    employer_id = serializers.IntegerField(required=True)
    room_id = serializers.IntegerField(required=True)

    class Meta:
        model = Room
        fields = ['employer_id', 'room_ id']

    def delete(self, instance, validated_data):
        employer_id = validated_data.get('employer_id')
        room_id = validated_data.get('room_id')

        if not Employer.objects.filter(id=employer_id).exists():
            raise serializers.ValidationError("Employer not found")

        if not Room.objects.filter(id=room_id).exists():
            raise serializers.ValidationError("Room not found")

        employer = Employer.objects.get(id=employer_id)
        room = Room.objects.get(id=room_id)

        if employer.is_admin_staff:
            room.delete()
            return room
        else:
            raise serializers.ValidationError("You are not allowed to delete this room")
        





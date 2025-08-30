from rest_framework import serializers
from .models import Reservation
from customers.serializers import CustomerSerializer
from rooms.serializers import RoomSerializer
from django.utils import timezone
from datetime import datetime
from project.celery import send_email_task
from rooms.models import Room
from .models import Reservation
from customers.models import Customer
from django.db import transaction
import secrets

class ReservationSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer(read_only=True)
    room = RoomSerializer(read_only=True)
    
    class Meta:
        model = Reservation
        fields = [
            'id', 'customer', 'room', 'check_in', 'check_out', 'booking_status'
        ]
        read_only_fields = ['id']

class ReservationCreateSerializer(serializers.ModelSerializer):
    room_id = serializers.IntegerField(required=True)
    customer_id = serializers.IntegerField(required=True)
    check_in = serializers.DateField(required=True)
    check_out = serializers.DateField(required=True)
    booking_status = serializers.CharField(required=False)

    class Meta:
        model = Reservation
        fields = ['room_id', 'customer_id', 'check_in', 'check_out', 'booking_status']

    def create(self, validated_data):
        room_id = validated_data.pop('room_id')
        customer_id = validated_data.pop('customer_id')

        room = Room.objects.get(id=room_id)
        customer = Customer.objects.get(id=customer_id)

        if not room.is_available:
            raise serializers.ValidationError("Room is not available")

        #if already have onther reservation in the same room in the same period
        conflicting_reservations = Reservation.objects.filter(
            room_id=room_id,
            check_in__lt=validated_data['check_out'],
            check_out__gt=validated_data['check_in'],
            booking_status__in=['Confirmed']
        )

        if conflicting_reservations.exists():
            raise serializers.ValidationError("Room is not available")
        
        #create reservation
        with transaction.atomic():
            reservation_code = secrets.token_hex(10)
            reservation = Reservation.objects.create(
                customer=customer,
                room=room,
                check_in=validated_data['check_in'],
                check_out=validated_data['check_out'],
                booking_status='Confirmed',
                reservation_code=reservation_code
            )
            
            room.save()
            
            self.send_confirmation_email(reservation)
            
            return reservation

    
    def send_confirmation_email(self, reservation):
        _message = f"""
            Hello {reservation.customer.user.name},
            Your reservation has been confirmed successfully!
            Reservation details:
            Reservation Code: {reservation.reservation_code}
            Customer: {reservation.customer.user.name}
            Room: {reservation.room.number}
            Check-in: {reservation.check_in.strftime('%d/%m/%Y')}
            Check-out: {reservation.check_out.strftime('%d/%m/%Y')}
            Booking Status: {reservation.booking_status}
            Best regards,
            {reservation.room.hotel.name} team
        """
        #send email
        send_email_task.delay(
            'reservation_confirmation',
            _message,
            [reservation.customer.user.email],
            reservation.room.hotel.email
        )
        return True
    

#TODO: update reservation
#TODO: cancel reservation
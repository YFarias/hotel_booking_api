from rest_framework import serializers
from django.db import transaction
from django.shortcuts import get_object_or_404
import secrets

from .models import Reservation
from customers.models import Customer
from rooms.models import Room
from customers.serializers import CustomerSerializer
from rooms.serializers import RoomSerializer
from project.celery import send_email_task


class ReservationSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer(read_only=True)
    room = RoomSerializer(read_only=True)

    class Meta:
        model = Reservation
        fields = ['id', 'customer', 'room', 'check_in', 'check_out', 'booking_status']
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

    def validate(self, attrs):
        ci, co = attrs['check_in'], attrs['check_out']
        if co <= ci:
            raise serializers.ValidationError({"check_out": "check_out must be after check_in."})
        return attrs

    def create(self, validated_data):
        room_id = validated_data.pop('room_id')
        customer_id = validated_data.pop('customer_id')
        ci, co = validated_data['check_in'], validated_data['check_out']

        # Trava a linha do quarto e checa conflitos dentro da transação
        with transaction.atomic():
            room = get_object_or_404(Room.objects.select_for_update(), id=room_id)
            customer = get_object_or_404(Customer, id=customer_id)

            # Conflito: qualquer reserva Confirmed que intercepte [ci, co]
            conflict_exists = Reservation.objects.select_for_update().filter(
                room_id=room_id,
                check_in__lt=co,
                check_out__gt=ci,
                booking_status='Confirmed',
            ).exists()
            if conflict_exists:
                raise serializers.ValidationError({"room_id": "Room is not available for the selected period."})

            reservation = Reservation.objects.create(
                customer=customer,
                room=room,
                check_in=ci,
                check_out=co,
                booking_status=validated_data.get('booking_status', 'Pending'),
                reservation_code=secrets.token_hex(10),
            )

        # E-mail após criar (fora da transação)
        self._send_email(reservation)
        return reservation

    def _send_email(self, reservation: Reservation):
        is_confirmed = (reservation.booking_status == 'Confirmed')
        subject = "Reservation Confirmation" if is_confirmed else "Reservation Received"

        msg = (
            f"Hello {reservation.customer.user.name},\n\n"
            f"{'Your reservation has been confirmed successfully!' if is_confirmed else 'We received your reservation.'}\n\n"
            "Reservation details:\n"
            f"Reservation Code: {reservation.reservation_code}\n"
            f"Hotel: {reservation.room.hotel.name}\n"
            f"Room: {reservation.room.number}\n"
            f"Check-in: {reservation.check_in:%d/%m/%Y}\n"
            f"Check-out: {reservation.check_out:%d/%m/%Y}\n"
            f"Status: {reservation.booking_status}\n\n"
            f"Best regards,\n{reservation.room.hotel.name} team"
        )

        # Usa DEFAULT_FROM_EMAIL (não passamos from_email)
        send_email_task.delay(subject, msg, [reservation.customer.user.email])



    

#TODO: update reservation
#TODO: cancel reservation
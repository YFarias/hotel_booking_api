import os

import django

#dependency
from django.db import models
from django.utils import timezone
from django.conf import settings
from rooms.models import Room
from customers.models import Customer



class Reservation(models.Model):
    customer = models.ForeignKey(
        Customer, 
        on_delete=models.CASCADE, 
        verbose_name="customer",
        related_name="reservation_customer_set"
    )
    
    room = models.ForeignKey(
        Room, 
        on_delete=models.CASCADE, 
        verbose_name="room",
        related_name="reservation_room_set"
    )

    check_in = models.DateField("check_in", null=True, blank=True)
    check_out = models.DateField("check_out", null=True, blank=True)
    booking_status = models.CharField("booking_status", max_length=20, null=True, blank=True, default="Pending")

    def __str__(self):
        return f"{self.customer.user.email} - {self.room.alias}"
    
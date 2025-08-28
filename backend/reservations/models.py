import os

import django

#dependency
from django.db import models
from django.utils import timezone
from django.conf import settings
from rooms.models import Room
from customers.models import Customer    


Customer = settings.AUTH_USER_MODEL

class Reservation(models.Model):
    customer = models.ForeignKey(
        Customer, 
        on_delete=models.CASCADE, 
        verbose_name="customer",
        related_name="customer_reservation_set"
    )
    room = models.ForeignKey(
        Room, 
        on_delete=models.CASCADE, 
        verbose_name="room",
        related_name="room_reservation_set"
    )

    check_in = models.DateField("check_in", null=True, blank=True)
    check_out = models.DateField("check_out", null=True, blank=True)
    status = models.CharField("status", max_length=20, null=True, blank=True)

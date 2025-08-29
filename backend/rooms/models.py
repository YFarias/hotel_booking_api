import os

import django

#dependency
from django.db import models    
from django.conf import settings
from hotels.models import Hotel


Customer = settings.AUTH_USER_MODEL

class Room(models.Model):
    hotel = models.ForeignKey(
        Hotel, 
        on_delete=models.CASCADE, 
        verbose_name="hotel",
        related_name="room_hotel_set"
    )
    number = models.IntegerField("number", null=False, blank=False)
    complement = models.CharField("complement", max_length=255, null=True, blank=True)
    is_available = models.BooleanField("is_available", default=True)

    def __str__(self):
        return self.number

    @property
    def alias(self):
        return f"{self.hotel.name} - {self.number} {self.complement}"
    
    @property
    def status(self):
        return "Available" if self.is_available else "Not Available"
    
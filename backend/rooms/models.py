import os

import django

#dependency
from django.db import models    
from django.conf import settings
from hotels.models import Hotel


Customer = settings.AUTH_USER_MODEL

class Room(models.Model):
    number = models.IntegerField("number", null=False, blank=False)
    hotel = models.ForeignKey(
        Hotel, 
        on_delete=models.CASCADE, 
        verbose_name="hotel",
        related_name="hotel_room_set"
    )
    status = models.CharField("status", max_length=20, null=False, blank=False, default="available")


    def __str__(self):
        return self.number
import os

import django

#dependency
from django.db import models    
from users.models import User
from hotels.models import Hotel


class Employer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="employer_user_set")
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name="employer_hotel_set")
    role = models.CharField(max_length=20, null=True, blank=True)
    is_admin_staff = models.BooleanField(default=False)
    
    def __str__(self):
        return self.user.name
    
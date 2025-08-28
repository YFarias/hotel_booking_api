import os

import django

#dependency
from django.db import models



class Hotel(models.Model):
    name = models.CharField("name", max_length=100, null=False, blank=False)
    email = models.EmailField("email", unique=True, null=False, blank=False)
    phone = models.CharField("phone", max_length=20, null=False, blank=False)
    address = models.TextField("address", null=False, blank=False)

    def __str__(self):
        return self.name
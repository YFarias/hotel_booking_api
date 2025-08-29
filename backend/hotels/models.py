import os

import django

#dependency
from django.db import models
from django.utils import timezone
from django.conf import settings


class Hotel(models.Model):
    name = models.CharField("name", max_length=255, null=False, blank=False)
    email = models.EmailField("email", null=False, blank=False)
    phone = models.CharField("phone", max_length=255, null=False, blank=False)
    street = models.CharField("street", max_length=255, null=False, blank=False)
    number = models.CharField("number", max_length=255, null=False, blank=False)
    complement = models.CharField("complement", max_length=255, null=True, blank=True)
    city = models.CharField("city", max_length=255, null=False, blank=False)
    state = models.CharField("state", max_length=255, null=False, blank=False)
    zip_code = models.CharField("zip_code", max_length=255, null=False, blank=False)
    website = models.URLField("website", null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Hotel"
        verbose_name_plural = "Hotels"

    @property
    def full_address(self):
        return f"{self.street}, {self.number}, {self.complement}, {self.city}, {self.state}, {self.zip_code}"

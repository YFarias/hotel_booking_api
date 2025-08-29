# customers/models.py (ou dentro do app que preferir)
from django.conf import settings
from django.db import models
# from model_utils.models import TimeStampedModel  # se quiser timestamps

class Customer(models.Model):  # ou TimeStampedModel
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="customer_user_set", 
    )
    preferences = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"Customer<{self.user.email}>"

    class Meta:
        verbose_name = "Customer"
        verbose_name_plural = "Customers"

    @property
    def name(self):
        return f"{self.user.name}"

    @property
    def email(self):
        return f"{self.user.email}"

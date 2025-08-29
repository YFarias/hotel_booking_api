from django.contrib import admin
from .models import Employer


@admin.register(Employer)
class EmployerAdmin(admin.ModelAdmin):
    list_display = ("user", "hotel", "role", "is_admin_staff")
    search_fields = ("user__email", "hotel__name")
    ordering = ("hotel__name",)
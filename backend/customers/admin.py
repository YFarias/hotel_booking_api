from django.contrib import admin
from .models import Customer


#Simple admin view
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("user", "preferences")
    search_fields = ("user__email", "user__name")
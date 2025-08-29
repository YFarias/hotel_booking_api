from django.contrib import admin
from .models import Hotel


#simple admin view
@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone", "full_address")
    search_fields = ("name", "email", "phone", "city", "state", "zip_code")
    list_filter = ("city", "state")
    ordering = ("name",)
    readonly_fields = ("full_address",)

    

   
from django.contrib import admin
from .models import Room


from django.contrib import admin
from .models import Room


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("hotel", "number", "complement", "is_available", "status")
    search_fields = ("hotel__name", "complement", "number_str")
    list_filter = ("hotel", "is_available")
    ordering = ("hotel__name", "number")

    def number_str(self, obj):
        return str(obj.number)
    number_str.admin_order_field = "number"
    number_str.short_description = "Room Number"

    def status(self, obj):
        return "Available" if obj.is_available else "Not Available"
    status.short_description = "Status"
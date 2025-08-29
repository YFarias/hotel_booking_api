from django.contrib import admin
from .models import Room


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("hotel", "number", "complement", "is_available", "status")
    search_fields = ("hotel__name", "number", "complement")
    list_filter = ("hotel", "is_available")
    ordering = ("hotel__name", "number")
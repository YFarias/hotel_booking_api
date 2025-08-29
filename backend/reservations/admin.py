from django.contrib import admin
from .models import Reservation

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ("customer", "room", "check_in", "check_out", "booking_status")
    search_fields = ("customer__user__email", "room__alias")
    list_filter = ("booking_status", "check_in", "check_out")
    ordering = ("customer__user__email", "room__alias")
    readonly_fields = ("customer", "room", "check_in", "check_out", "booking_status")
    search_fields = ("customer__user__email", "room__alias")

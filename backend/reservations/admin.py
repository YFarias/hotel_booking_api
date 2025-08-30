from django.contrib import admin
from .models import Reservation

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    # Show in lists
    list_display = ("customer", "room", "check_in", "check_out", "booking_status")

    # Search by real fields
    search_fields = (
        "customer__user__email",
        "room__number",
        "room__hotel__name",
        "room__complement",
    )

    # Filters
    list_filter = ("booking_status", "check_in", "check_out")

    # Order by real fields (customer email and room number)
    ordering = ("customer__user__email", "room__number")

    # Do not make the required fields readonly
    # If you want to keep something readonly, keep only 'booking_status' (if it is a property/calculated field)
    readonly_fields = ("booking_status",)

    # Optional: control the order/visibility of the fields in the form
    fields = ("customer", "room", "check_in", "check_out", "booking_status")

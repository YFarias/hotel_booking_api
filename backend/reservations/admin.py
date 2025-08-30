# reservations/admin.py
from django.contrib import admin, messages
from .models import Reservation
from project.celery import send_email_task


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ("customer", "room", "check_in", "check_out", "booking_status")
    fields = ("customer", "room", "check_in", "check_out", "booking_status")

    def _build_confirmation_message(self, res: Reservation) -> str:
        return (
            f"Hello {res.customer.user.name},\n\n"
            f"Your reservation has been confirmed successfully!\n\n"
            f"Reservation Code: {res.reservation_code}\n"
            f"Customer: {res.customer.user.name}\n"
            f"Hotel: {res.room.hotel.name}\n"
            f"Room: {res.room.number}\n"
            f"Check-in: {res.check_in:%d/%m/%Y}\n"
            f"Check-out: {res.check_out:%d/%m/%Y}\n"
            f"Booking Status: {res.booking_status}\n\n"
            f"Best regards,\n{res.room.hotel.name} team"
        )

    def save_model(self, request, obj, form, change):
        send_confirmation = False
        if change:
            if "booking_status" in form.changed_data:
                prev_status = Reservation.objects.only("booking_status").get(pk=obj.pk).booking_status
                send_confirmation = prev_status != "Confirmed" and obj.booking_status == "Confirmed"
        else:
            send_confirmation = obj.booking_status == "Confirmed"

        super().save_model(request, obj, form, change)

        if send_confirmation:
            msg = self._build_confirmation_message(obj)
            send_email_task.delay("Reservation Confirmation", msg, [obj.customer.user.email])
            self.message_user(request, "Confirmation e-mail queued via Celery.", level=messages.SUCCESS)


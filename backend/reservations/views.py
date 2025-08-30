from rest_framework import viewsets, permissions, filters, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Reservation
from .serializers import (
    ReservationSerializer,
    ReservationCreateSerializer,
)

class ReservationViewSet(viewsets.ModelViewSet):
    """
    CRUD
    - GET list/retrieve -> ReservationSerializer
    - POST create       -> ReservationCreateSerializer
    - DELETE destroy    -> ReservationSerializer
    """
    queryset = Reservation.objects.all()
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['customer__user__name', 'room__number', 'booking_status']
    ordering_fields = ['id', 'check_in', 'check_out']
    ordering = ['-check_in']

    # Map
    # TODO: add update serializer
    action_serializers = {
        'list': ReservationSerializer,
        'retrieve': ReservationSerializer,
        'create': ReservationCreateSerializer,
        'destroy': ReservationSerializer,
    }

    def get_serializer_class(self):
        return self.action_serializers.get(self.action, ReservationSerializer)

    def get_permissions(self):
        # All operations for authenticated users
        return [IsAuthenticated()]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user

        if not user.is_authenticated:
            return qs.none()

        if user.is_superuser:
            return qs

        # Customer only see his own reservations
        if hasattr(user, 'customer_user_set') and user.customer_user_set.exists():
            customer = user.customer_user_set.first()
            return qs.filter(customer=customer)

        # Employer see reservations of the hotel where he works
        if hasattr(user, 'employer_user_set') and user.employer_user_set.exists():
            employer = user.employer_user_set.first()
            return qs.filter(room__hotel=employer.hotel)

        return qs.none()

    # ---------- CREATE ----------
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        reservation = serializer.save()
        return Response(ReservationSerializer(reservation).data, status=status.HTTP_201_CREATED)

    # ---------- DELETE ----------
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Mark the room as available when deleting
        instance.room.is_available = True
        instance.room.save()
        
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
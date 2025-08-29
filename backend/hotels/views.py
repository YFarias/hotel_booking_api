from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from .models import Hotel
from .serializers import (
    HotelSerializer,
    HotelCreateSerializer,
    HotelUpdateSerializer,
)

class HotelViewSet(viewsets.ModelViewSet):
    queryset = Hotel.objects.all()
    action_serializers = {
        'list': HotelSerializer,
        'retrieve': HotelSerializer,
        'create': HotelCreateSerializer,
        'update': HotelUpdateSerializer,
        'partial_update': HotelUpdateSerializer,
        'destroy': HotelSerializer,
    }

    def get_serializer_class(self):
        return self.action_serializers.get(self.action, HotelSerializer)

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated(), IsAdminUser()]
        if self.action in ('update', 'partial_update', 'destroy'):
            return [IsAuthenticated(), IsAdminUser()]
        return [IsAuthenticated()]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user

        if not user.is_authenticated:
            return qs.none()

        if user.is_superuser or user.is_staff:
            return qs

        if hasattr(user, 'employer_user_set') and user.employer_user_set.exists():
            employer = user.employer_user_set.first()
            return qs.filter(id=employer.hotel.id)

        if getattr(user, 'is_customer', False):
            return qs

        return qs.none()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        hotel = serializer.save()
        return Response(HotelSerializer(hotel).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial, context=self.get_serializer_context()
        )
        serializer.is_valid(raise_exception=True)
        hotel = serializer.save()
        return Response(HotelSerializer(hotel).data, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance = self.get_object()
        
        #delete all works
        Employer.objects.filter(hotel=instance).delete()

        #delete the hotel
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
from rest_framework import viewsets, permissions, filters, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError

from .models import Room
from .serializers import (
    RoomSerializer,
    RoomCreateSerializer,
    RoomUpdateSerializer,
    RoomDeleteSerializer,
)

class RoomViewSet(viewsets.ModelViewSet):
    """
     CRUD for rooms with specific operations.
    - GET list/retrieve -> RoomSerializer (read only)
    - POST create       -> RoomCreateSerializer (only admin_staff of hotel)
    - PUT/PATCH update  -> RoomUpdateSerializer (only admin_staff of hotel)
    - DELETE destroy    -> RoomDeleteSerializer (only admin_staff of hotel)
    """
    queryset = Room.objects.all()
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['number', 'complement', 'hotel__name']
    ordering_fields = ['id', 'number', 'hotel__name', 'is_available']
    ordering = ['hotel__name', 'number']

    # Mapping of serializers by action
    action_serializers = {
        'list': RoomSerializer,
        'retrieve': RoomSerializer,
        'create': RoomCreateSerializer,
        'update': RoomUpdateSerializer,
        'partial_update': RoomUpdateSerializer,
        'destroy': RoomDeleteSerializer,
    }

    def get_serializer_class(self):
        return self.action_serializers.get(self.action, RoomSerializer)

    def get_permissions(self):
        # Creation only for authenticated users (validation of admin_staff in serializer)
        if self.action == 'create':
            return [IsAuthenticated()]
        # Write operations only for authenticated users
        if self.action in ('update', 'partial_update', 'destroy'):
            return [IsAuthenticated()]
        # Read for authenticated users
        return [IsAuthenticated()]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user

        if not user.is_authenticated:
            return qs.none()

        if user.is_superuser or user.is_staff:
            return qs

        # Employer see rooms of hotel where he works
        if hasattr(user, 'employer_user_set') and user.employer_user_set.exists():
            employer = user.employer_user_set.first()
            return qs.filter(hotel=employer.hotel)

        # Customer see only available rooms 
        if getattr(user, 'is_customer', False):
            return qs.filter(is_available=True)

        return qs.none()

    # ---------- CREATE ----------
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        room = serializer.save()
        return Response(RoomSerializer(room).data, status=status.HTTP_201_CREATED)

    # ---------- UPDATE / PATCH ----------
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        serializer = self.get_serializer(
            instance, data=request.data, partial=partial, context=self.get_serializer_context()
        )
        serializer.is_valid(raise_exception=True)
        room = serializer.save()
        return Response(RoomSerializer(room).data, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    # ---------- DELETE ----------
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        serializer = self.get_serializer(instance=instance, context=self.get_serializer_context())
        serializer.delete(instance, {})
        return Response(status=status.HTTP_204_NO_CONTENT)

    # ---------- EXTRA ACTIONS ----------
    @action(detail=False, methods=['get'], url_path='available')
    def available_rooms(self, request):
        qs = self.get_queryset().filter(is_available=True)
        serializer = RoomSerializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='by-hotel')
    def rooms_by_hotel(self, request):
        hotel_id = request.query_params.get('hotel_id', '')
        
        if not hotel_id:
            return Response(
                {"detail": "Parameter 'hotel_id' is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        qs = self.get_queryset().filter(hotel_id=hotel_id)
        serializer = RoomSerializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='toggle-availability')
    def toggle_availability(self, request, pk=None):
        
        instance = self.get_object()
        
        #verify if the user is admin of hotel or superuser
        try:
            from employers.models import Employer
            employer = Employer.objects.get(user=request.user, hotel=instance.hotel)
            if not employer.is_admin_staff:
                return Response(
                    {"detail": "Only admin of hotel or superuser can change availability"}, 
                    status=status.HTTP_403_FORBIDDEN
                )
        except Employer.DoesNotExist:
            return Response(
                {"detail": "Usuário não é funcionário deste hotel"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        instance.is_available = not instance.is_available
        instance.save()
        return Response(RoomSerializer(instance).data)

    @action(detail=False, methods=['get'], url_path='search')
    def search_rooms(self, request):
        query = request.query_params.get('q', '')
        hotel_name = request.query_params.get('hotel', '')
        available_only = request.query_params.get('available', 'true').lower() == 'true'
        
        qs = self.get_queryset()
        
        if query:
            qs = qs.filter(number__icontains=query) | qs.filter(complement__icontains=query)
        if hotel_name:
            qs = qs.filter(hotel__name__icontains=hotel_name)
        if available_only:
            qs = qs.filter(is_available=True)
        
        serializer = RoomSerializer(qs, many=True)
        return Response(serializer.data)
from rest_framework import viewsets, permissions, filters, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError

from .models import Employer
from .serializers import (
    EmployerSerializer,
    EmployerCreateSerializer,
    EmployerUpdateSerializer,
)

class EmployerViewSet(viewsets.ModelViewSet):
    queryset = Employer.objects.all()
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['user__name', 'user__email', 'user__phone', 'hotel__name', 'role']
    ordering_fields = ['id', 'user__name', 'hotel__name', 'role']
    ordering = ['user__name']

    # Mapeamento de serializers por ação
    action_serializers = {
        'list': EmployerSerializer,
        'retrieve': EmployerSerializer,
        'create': EmployerCreateSerializer,
        'update': EmployerUpdateSerializer,
        'partial_update': EmployerUpdateSerializer,
        'destroy': EmployerSerializer,
    }

    def get_serializer_class(self):
        return self.action_serializers.get(self.action, EmployerSerializer)

    def get_permissions(self):
        # Creation only for admin/staff
        if self.action == 'create':
            return [IsAuthenticated(), IsAdminUser()]
        # Write operations only for admin/staff
        if self.action in ('update', 'partial_update', 'destroy'):
            return [IsAuthenticated(), IsAdminUser()]
        # Read for authenticated users
        return [IsAuthenticated()]

    def get_queryset(self):
        #scope by role:
        #- superuser: see all
        #- admin_staff: see employees of your hotel
        #- common employer: see only yourself
        qs = super().get_queryset()
        user = self.request.user

        if not user.is_authenticated:
            return qs.none()

        if user.is_superuser:
            return qs

        if hasattr(user, 'employer_user_set') and user.employer_user_set.exists():
            employer = user.employer_user_set.first()
            if employer.is_admin_staff:
                # Admin of the hotel sees all employees of the hotel
                return qs.filter(hotel=employer.hotel)
            else:
                # Common employer sees only himself
                return qs.filter(user=user)

        return qs.none()

    # ---------- CREATE ----------
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        employer = serializer.save()
        return Response(EmployerSerializer(employer).data, status=status.HTTP_201_CREATED)

    # ---------- UPDATE / PATCH ----------
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        serializer = self.get_serializer(
            instance, data=request.data, partial=partial, context=self.get_serializer_context()
        )
        serializer.is_valid(raise_exception=True)
        employer = serializer.save()
        return Response(EmployerSerializer(employer).data, status=status.HTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    # ---------- DELETE ----------
    def destroy(self, request, *args, **kwargs): 
        instance = self.get_object()
        
        if instance.user == request.user and not request.user.is_superuser:
            return Response(
                {"detail": "You cannot delete your own account."}, 
                status=status.HTTP_403_FORBIDDEN
            )

        # Delete the employer
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

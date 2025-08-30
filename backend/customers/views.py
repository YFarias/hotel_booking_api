from rest_framework import viewsets, permissions, filters, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError

from .models import Customer
from .serializers import (
    CustomerSerializer,
    CustomerCreateSerializer,
    CustomerUpdateSerializer,
)

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['user__name', 'user__email', 'user__phone']
    ordering_fields = ['id', 'user__name', 'user__email']
    ordering = ['user__name']

    # map serializers by action
    action_serializers = {
        'list': CustomerSerializer,
        'retrieve': CustomerSerializer,
        'create': CustomerCreateSerializer,
        'update': CustomerUpdateSerializer,
        'partial_update': CustomerUpdateSerializer,
        'destroy': CustomerSerializer,
    }

    def get_serializer_class(self):
        return self.action_serializers.get(self.action, CustomerSerializer)

    def get_permissions(self):
        # public creation
        if self.action == 'create':
            return [AllowAny()]
        # write operations only for admin/staff
        if self.action in ('update', 'partial_update', 'destroy'):
            return [IsAuthenticated(), IsAdminUser()]
        # read for authenticated users
        return [IsAuthenticated()]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user

        if not user.is_authenticated:
            return qs.none()

        if user.is_superuser or user.is_staff:
            return qs

        # customer can only see his own data
        if getattr(user, 'is_customer', False):
            return qs.filter(user=user)

        return qs.none()

    # ---------- CREATE ----------
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        customer = serializer.save()
        return Response(CustomerSerializer(customer).data, status=status.HTTP_201_CREATED)

    # ---------- UPDATE / PATCH ----------
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        # validation: check if the user_id in the body corresponds to the customer in the URL
        body_user_id = request.data.get('user_id')
        if body_user_id and int(body_user_id) != instance.user.id:
            raise ValidationError({"user_id": "User ID não corresponde ao customer da URL"})

        serializer = self.get_serializer(
            instance, data=request.data, partial=partial, context=self.get_serializer_context()
        )
        serializer.is_valid(raise_exception=True)
        customer = serializer.save()
        return Response(CustomerSerializer(customer).data, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    # ---------- DELETE ----------
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # protection: do not allow customer to delete himself (only admin)
        if instance.user == request.user and not request.user.is_staff:
            return Response(
                {"detail": "Você não pode deletar sua própria conta."}, 
                status=status.HTTP_403_FORBIDDEN
            )

        # delete the customer (the user remains)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    # ---------- EXTRA ACTIONS ----------
    @action(detail=False, methods=['get'], url_path='me')
    def me(self, request):
        """
        Retorna o customer do usuário logado.
        """
        if not request.user.is_authenticated:
            return Response({"detail": "Usuário não autenticado"}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            customer = Customer.objects.get(user=request.user)
            serializer = CustomerSerializer(customer)
            return Response(serializer.data)
        except Customer.DoesNotExist:
            return Response({"detail": "Customer não encontrado"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'], url_path='update-preferences')
    def update_preferences(self, request, pk=None):
        """
        Atualiza apenas as preferências de um customer específico.
        """
        instance = self.get_object()
        preferences = request.data.get('preferences', {})
        
        if not isinstance(preferences, dict):
            return Response(
                {"detail": "Preferências devem ser um objeto JSON"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        instance.preferences = preferences
        instance.save()
        return Response(CustomerSerializer(instance).data)

    @action(detail=False, methods=['get'], url_path='search')
    def search_customers(self, request):
        """
        Advanced search for customers (only for admin/staff).
        """
        if not request.user.is_staff:
            return Response(
                {"detail": "Access denied"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        query = request.query_params.get('q', '')
        if not query:
            return Response({"detail": "Parameter 'q' is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        customers = Customer.objects.filter(
            user__name__icontains=query
        ) | Customer.objects.filter(
            user__email__icontains=query
        ) | Customer.objects.filter(
            user__phone__icontains=query
        )
        
        serializer = CustomerSerializer(customers, many=True)
        return Response(serializer.data)
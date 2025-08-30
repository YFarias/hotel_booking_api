# users/views.py
from django.contrib.auth import get_user_model
from rest_framework import viewsets, permissions, filters, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError

from .serializers import (
    UserSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
    UserDeleteSerializer,
    UserPasswordResetSerializer,
    UserLoginSerializer,
    UserLogoutSerializer,
)

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    """
    CRUD for users + auxiliary actions (login, logout, password_reset).
    - GET list/retrieve -> UserSerializer (read only)
    - POST create       -> UserCreateSerializer
    - PUT/PATCH update  -> UserUpdateSerializer (requires 'id' in body; checks with URL)
    - DELETE destroy    -> UserDeleteSerializer (uses instance from URL)
    - POST login        -> /users/login/
    - POST logout       -> /users/logout/
    - POST password_reset -> /users/password-reset/
    """
    queryset = User.objects.all()
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "email", "phone"]
    ordering_fields = ["id", "name", "email"]
    ordering = ["name"]

    # map 
    action_serializers = {
        "list": UserSerializer,
        "retrieve": UserSerializer,
        "create": UserCreateSerializer,
        "update": UserUpdateSerializer,
        "partial_update": UserUpdateSerializer,
        "destroy": UserDeleteSerializer,
        # custom actions
        "login": UserLoginSerializer,
        "logout": UserLogoutSerializer,
        "password_reset": UserPasswordResetSerializer,
    }

    def get_serializer_class(self):
        return self.action_serializers.get(self.action, UserSerializer)

    def get_permissions(self):
        # public actions
        if self.action in ("login", "logout", "password_reset"):
            return [AllowAny()]
        # write only for staff/admin
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [IsAuthenticated(), IsAdminUser()]
        # read only for authenticated
        return [IsAuthenticated()]

    def get_queryset(self):
        """
            Escopo por papel:
            - superuser: vê todos
            - customer: vê somente a si mesmo
            - employer: ajuste a regra do seu domínio aqui (placeholder -> none)
        """
        qs = super().get_queryset()
        _user = self.request.user

        if not _user.is_authenticated:
            return qs.none()

        if _user.is_superuser:
            return qs

        if getattr(_user, "is_customer", False):
            return qs.filter(id=_user.id)

        if getattr(_user, "is_employer", False):
            return qs.none()

        return qs.none()

    # ---------- CREATE ----------
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)

    # ---------- UPDATE / PATCH ----------
    def update(self, request, *args, **kwargs):
        """
        Requires 'id' in body and checks with the id in the URL.
        Calls UserUpdateSerializer.update(), which still searches/updates via id.
        """
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        # check URL x payload (prevents updating another user by mistake)
        body_id = request.data.get("id")
        if body_id is None:
            raise ValidationError({"id": "Required field in request body."})
        if int(body_id) != int(instance.id):
            raise ValidationError({"id": "ID in request body does not match the resource in the URL."})

        serializer = self.get_serializer(
            instance, data=request.data, partial=partial, context=self.get_serializer_context()
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)

    # ---------- DELETE ----------
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # extra protection: prevent deleting superuser unless the deleting user is superuser 
        if instance.is_superuser and not request.user.is_superuser:
            return Response({"detail": "Superuser deletion is not allowed."}, status=status.HTTP_403_FORBIDDEN)
        # optional: block self-deletion of non-superuser
        if instance == request.user and not request.user.is_superuser:
            return Response({"detail": "You cannot delete yourself."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(instance=instance, context=self.get_serializer_context())
        # your serializer expects 'delete(instance)'
        serializer.delete(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    # ---------- AÇÕES EXTRAS ----------
    @action(detail=False, methods=["post"], url_path="login", permission_classes=[AllowAny])
    def login(self, request):
        """
        Authenticates user and (optionally) emits tokens JWT via SimpleJWT.
        """
        s = self.get_serializer(data=request.data)
        s.is_valid(raise_exception=True)
        user = s.validated_data["user"]

        # If using SimpleJWT, generate tokens:
        tokens = None
        try:
            from rest_framework_simplejwt.tokens import RefreshToken
            refresh = RefreshToken.for_user(user)
            tokens = {"refresh": str(refresh), "access": str(refresh.access_token)}
        except Exception:
            # SimpleJWT not installed -> return minimal data
            tokens = {"detail": "SimpleJWT not installed. Return tokens according to your auth provider."}

        return Response(
            {
                "user": UserSerializer(user).data,
                **tokens,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["post"], url_path="logout", permission_classes=[AllowAny])
    def logout(self, request):
        """
        Invalida tokens (se usar SimpleJWT, faz blacklist do refresh).
        """
        s = self.get_serializer(data=request.data)
        s.is_valid(raise_exception=True)

        try:
            from rest_framework_simplejwt.tokens import RefreshToken
            refresh = s.validated_data["refresh"]
            token = RefreshToken(refresh)
            token.blacklist()  # requer SimpleJWT + blacklist app
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            # Without SimpleJWT/blacklist: just respond OK
            return Response({"detail": "Logout performed (without blacklist)."}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="password-reset", permission_classes=[AllowAny])
    def password_reset(self, request):
        """
        Validates the existence of the email (actual email sending depends on your infrastructure).
        """
        s = self.get_serializer(data=request.data)
        s.is_valid(raise_exception=True)
        # Here you would trigger email/reset token sending.
        return Response({"detail": "If the email exists, we will send reset instructions."}, status=status.HTTP_200_OK)


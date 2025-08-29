from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
]


# URLs:
# http://127.0.0.1:8000 GET/POST /api/users/ - list/create users
# http://127.0.0.1:8000 GET/PUT/PATCH/DELETE /api/users/1/ - operations on specific user
# http://127.0.0.1:8000 POST /api/users/login/ - login
# http://127.0.0.1:8000 POST /api/users/logout/ - logout
# http://127.0.0.1:8000 POST /api/users/password-reset/ - reset password
# http://127.0.0.1:8000 POST /api/token/ - get JWT token
# http://127.0.0.1:8000 POST /api/token/refresh/ - refresh JWT token
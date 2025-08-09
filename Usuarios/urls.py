"""
URL configuration for backendPruebaTaveron project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)
from .serializers import MyTokenObtainPairView
from .views import (
    ProtegidaView, 
    AdminView, 
    ModeratorView,
    UserListCreateView,
    UserDetailView,
    UserProfileView,
    UserRegisterView,
    ChangePasswordView,
    user_stats,
    toggle_user_status
)

urlpatterns = [
    # Autenticación JWT 
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # Registro público (sin autenticación requerida)
    path('register/', UserRegisterView.as_view(), name='user-register'),
    
    # Rutas de prueba existentes
    path('protegida/', ProtegidaView.as_view(), name='protegida'),
    path('admin/', AdminView.as_view(), name='admin'),
    path('moderator/', ModeratorView.as_view(), name='moderator'),
    
    # CRUD de usuarios (requiere autenticación)
    path('users/', UserListCreateView.as_view(), name='user-list-create'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    
    # Perfil del usuario autenticado
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    
    # Cambiar contraseña
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    
    # Estadísticas y administración de usuarios
    path('stats/', user_stats, name='user-stats'),
    path('users/<int:user_id>/toggle-status/', toggle_user_status, name='toggle-user-status'),
]

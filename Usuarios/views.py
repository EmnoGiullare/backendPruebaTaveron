from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import CustomUser
from .serializers import (
    UserSerializer, 
    UserCreateSerializer,
    UserRegisterSerializer,
    UserUpdateSerializer,
    PasswordChangeSerializer
)
from .permissions import IsAdminOrOwner, IsAdminOnly, IsModeratorOrAdmin

# Vista de registro público (sin autenticación requerida)
class UserRegisterView(generics.CreateAPIView):
    """
    Vista para registro público de usuarios
    No requiere autenticación - cualquier persona puede registrarse
    El rol siempre será 'user' por defecto
    """
    queryset = CustomUser.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny]  # Permite acceso sin autenticación
    
    def create(self, request, *args, **kwargs):
        """
        Override del método create para personalizar la respuesta
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Respuesta personalizada con información del usuario creado
        return Response({
            'message': 'Usuario registrado exitosamente',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'full_name': user.get_full_name(),
                'rol': user.rol,
                'phone': user.phone,
                'address': user.address,
                'created_at': user.created_at,
                'is_active': user.is_active
            },
            'info': 'Ya puedes iniciar sesión con tus credenciales'
        }, status=status.HTTP_201_CREATED)

# Vistas de prueba para verificar permisos y autenticación
class ProtegidaView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        content = {
            'mensaje': f'Hola {request.user.username}!',
            'user_info': {
                'id': request.user.id,
                'email': request.user.email,
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'rol': request.user.rol,
                'phone': request.user.phone,
                'address': request.user.address,
            }
        }
        return Response(content)

class AdminView(APIView):
    permission_classes = [IsAdminOnly]
    
    def get(self, request):
        return Response({
            'message': 'Solo para administradores (rol admin)',
            'user': {
                'username': request.user.username,
                'rol': request.user.rol,
                'is_staff': request.user.is_staff
            }
        })

class ModeratorView(APIView):
    permission_classes = [IsModeratorOrAdmin]
    
    def get(self, request):
        return Response({
            'message': 'Acceso para moderadores y administradores',
            'user': {
                'username': request.user.username,
                'rol': request.user.rol,
                'permissions': 'moderator_or_admin'
            }
        })

# Vistas CRUD
class UserListCreateView(generics.ListCreateAPIView):
    """
    Vista para listar usuarios (GET - solo admin) y crear nuevos usuarios (POST - solo admin)
    """
    queryset = CustomUser.objects.all()
    permission_classes = [IsAdminOnly] 
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserCreateSerializer
        return UserSerializer
    
    def get_queryset(self):
        """
        Solo administradores pueden ver la lista de usuarios
        """
        # Esta validación adicional por si acaso
        if not self.request.user.is_admin:
            return CustomUser.objects.none()
        
        return CustomUser.objects.all().order_by('-created_at')
    
    def list(self, request, *args, **kwargs):
        """
        Override del método list para agregar mensaje informativo
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        return Response({
            'message': 'Lista de todos los usuarios (solo disponible para administradores)',
            'count': queryset.count(),
            'users': serializer.data
        })

class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Vista para obtener, actualizar o eliminar un usuario específico
    Solo admins pueden ver cualquier usuario, usuarios regulares solo pueden ver su propio perfil
    Los usuarios pueden eliminar su propia cuenta
    """
    queryset = CustomUser.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsAdminOrOwner]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UserUpdateSerializer
        return UserSerializer
    
    def retrieve(self, request, *args, **kwargs):
        """
        Override del método retrieve para personalizar la respuesta
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        # Verificar si el usuario está accediendo a su propio perfil
        is_own_profile = instance == request.user
        
        response_data = {
            'message': 'Perfil propio' if is_own_profile else 'Perfil de usuario (vista de administrador)',
            'user': serializer.data
        }
        
        return Response(response_data)
    
    def perform_update(self, serializer):
        """
        Lógica personalizada antes de actualizar
        """
        user = self.get_object()
        request_user = self.request.user
        
        # Si no es admin y trata de cambiar el rol, no permitir
        if not request_user.is_admin and 'rol' in serializer.validated_data:
            if serializer.validated_data['rol'] != user.rol:
                del serializer.validated_data['rol']
        
        serializer.save()
    
    def destroy(self, request, *args, **kwargs):
        """
        Eliminar usuario con validaciones adicionales
        Permite que usuarios eliminen su propia cuenta y que admins eliminen cualquier cuenta
        """
        user = self.get_object()
        is_admin = request.user.is_admin
        is_own_account = user == request.user
        
        # Verificar permisos: debe ser admin O ser su propia cuenta
        if not is_admin and not is_own_account:
            return Response(
                {"error": "No tienes permisos para eliminar esta cuenta."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Validación especial para administradores
        if user.is_admin:
            admin_count = CustomUser.objects.filter(rol=CustomUser.RolChoices.ADMIN).count()
            
            # Prevenir que se elimine el último administrador
            if admin_count <= 1:
                return Response(
                    {"error": "No se puede eliminar el último administrador del sistema."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Si un admin se está eliminando a sí mismo, agregar confirmación especial
            if is_own_account:
                # Verificar si se envió confirmación adicional para auto-eliminación de admin
                confirmation = request.data.get('confirm_admin_deletion', False)
                if not confirmation:
                    return Response(
                        {
                            "error": "Para eliminar tu cuenta de administrador, debes incluir 'confirm_admin_deletion': true en la petición.",
                            "warning": "Esta acción es irreversible y perderás todos los privilegios de administrador."
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
        
        # Guardar información del usuario antes de eliminarlo para la respuesta
        user_info = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'rol': user.rol,
            'was_own_account': is_own_account
        }
        
        # Eliminar el usuario
        user.delete()
        
        # Respuesta personalizada según el caso
        if is_own_account:
            message = "Tu cuenta ha sido eliminada exitosamente. Lamentamos verte partir."
        else:
            message = f"Usuario '{user_info['username']}' eliminado exitosamente por el administrador."
        
        return Response({
            "message": message,
            "deleted_user": {
                "username": user_info['username'],
                "email": user_info['email'],
                "rol": user_info['rol']
            }
        }, status=status.HTTP_200_OK)

class UserProfileView(APIView):
    """
    Vista para obtener y actualizar el perfil del usuario autenticado
    Alternativa más simple para que los usuarios accedan a su propio perfil
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response({
            'message': 'Tu perfil personal',
            'user': serializer.data
        })
    
    def put(self, request):
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            # Los usuarios no admin no pueden cambiar su rol
            if not request.user.is_admin and 'rol' in serializer.validated_data:
                del serializer.validated_data['rol']
            
            serializer.save()
            return Response({
                'message': 'Perfil actualizado exitosamente',
                'user': serializer.data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request):
        """
        Permite actualizaciones parciales
        """
        return self.put(request)
    
    def delete(self, request):
        """
        Eliminar la propia cuenta del usuario autenticado
        """
        user = request.user
        
        # Validación especial para administradores
        if user.is_admin:
            admin_count = CustomUser.objects.filter(rol=CustomUser.RolChoices.ADMIN).count()
            
            # Prevenir que se elimine el último administrador
            if admin_count <= 1:
                return Response(
                    {"error": "No puedes eliminar tu cuenta porque eres el último administrador del sistema."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Solicitar confirmación especial para admin
            confirmation = request.data.get('confirm_admin_deletion', False)
            if not confirmation:
                return Response(
                    {
                        "error": "Para eliminar tu cuenta de administrador, debes incluir 'confirm_admin_deletion': true en la petición.",
                        "warning": "Esta acción es irreversible y perderás todos los privilegios de administrador."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Guardar info antes de eliminar
        user_info = {
            'username': user.username,
            'email': user.email,
            'rol': user.rol
        }
        
        # Eliminar cuenta
        user.delete()
        
        return Response({
            "message": "Tu cuenta ha sido eliminada exitosamente. Lamentamos verte partir.",
            "deleted_user": {
                "username": user_info['username'],
                "email": user_info['email'],
                "rol": user_info['rol']
            }
        }, status=status.HTTP_200_OK)

class ChangePasswordView(APIView):
    """
    Vista para cambiar la contraseña del usuario autenticado
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            return Response(
                {"message": "Contraseña cambiada exitosamente."},
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAdminOnly])
def user_stats(request):
    """
    Endpoint para obtener estadísticas de usuarios (solo administradores)
    """
    total_users = CustomUser.objects.count()
    active_users = CustomUser.objects.filter(is_active=True).count()
    admin_users = CustomUser.objects.filter(rol=CustomUser.RolChoices.ADMIN).count()
    regular_users = CustomUser.objects.filter(rol=CustomUser.RolChoices.USER).count()
    moderator_users = CustomUser.objects.filter(rol=CustomUser.RolChoices.MODERATOR).count()
    
    stats = {
        'total_users': total_users,
        'active_users': active_users,
        'inactive_users': total_users - active_users,
        'admin_users': admin_users,
        'regular_users': regular_users,
        'moderator_users': moderator_users,
        'message': 'Estadísticas del sistema (solo disponible para administradores)'
    }
    
    return Response(stats, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAdminOnly])
def toggle_user_status(request, user_id):
    """
    Endpoint para activar/desactivar usuarios (solo administradores)
    """
    try:
        user = CustomUser.objects.get(id=user_id)
        
        # Prevenir desactivar el último administrador
        if user.is_admin and user.is_active:
            active_admin_count = CustomUser.objects.filter(
                rol=CustomUser.RolChoices.ADMIN, 
                is_active=True
            ).count()
            if active_admin_count <= 1:
                return Response(
                    {"error": "No se puede desactivar el último administrador activo."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        user.is_active = not user.is_active
        user.save()
        
        status_text = "activado" if user.is_active else "desactivado"
        return Response(
            {"message": f"Usuario {status_text} exitosamente.", "is_active": user.is_active},
            status=status.HTTP_200_OK
        )
        
    except CustomUser.DoesNotExist:
        return Response(
            {"error": "Usuario no encontrado."},
            status=status.HTTP_404_NOT_FOUND
        )


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, BasePermission

class ProtegidaView(APIView):
    permission_classes = [IsAuthenticated]
    
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

# Permiso personalizado para administradores basado en rol
class IsAdminRole(BasePermission):
    """
    Permiso personalizado que permite acceso solo a usuarios con rol 'admin'
    """
    def has_permission(self, request, view):
        return (request.user and 
                request.user.is_authenticated and 
                hasattr(request.user, 'rol') and
                request.user.rol == 'admin')

# Permiso para moderadores y administradores
class IsModeratorOrAdmin(BasePermission):
    """
    Permiso que permite acceso a moderadores y administradores
    """
    def has_permission(self, request, view):
        return (request.user and 
                request.user.is_authenticated and 
                hasattr(request.user, 'rol') and
                request.user.rol in ['admin', 'moderator'])

class AdminView(APIView):
    permission_classes = [IsAuthenticated, IsAdminRole]
    
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
    permission_classes = [IsAuthenticated, IsModeratorOrAdmin]
    
    def get(self, request):
        return Response({
            'message': 'Acceso para moderadores y administradores',
            'user': {
                'username': request.user.username,
                'rol': request.user.rol,
                'permissions': 'moderator_or_admin'
            }
        })


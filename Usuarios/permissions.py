from rest_framework import permissions

class IsAdminOrOwner(permissions.BasePermission):
    """
    Permiso personalizado para permitir que solo los administradores 
    o el propio usuario puedan acceder a su información
    """
    
    def has_object_permission(self, request, view, obj):
        # Los administradores pueden hacer cualquier cosa
        if request.user.is_admin:
            return True
        
        # Los usuarios solo pueden acceder a su propia información
        return obj == request.user

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permiso que permite lectura a todos los usuarios autenticados,
    pero solo los administradores pueden crear, actualizar o eliminar
    """
    
    def has_permission(self, request, view):
        # Leer permisos para cualquier usuario autenticado
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        
        # Permisos de escritura solo para administradores
        return request.user.is_authenticated and request.user.is_admin

class IsAdminOnly(permissions.BasePermission):
    """
    Permiso que solo permite acceso a administradores
    """
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin

class IsModeratorOrAdmin(permissions.BasePermission):
    """
    Permiso que permite acceso a moderadores y administradores
    """
    
    def has_permission(self, request, view):
        return (request.user.is_authenticated and 
                (request.user.is_admin or request.user.rol == request.user.RolChoices.MODERATOR))

class IsAdminForListOrOwnerForDetail(permissions.BasePermission):
    """
    Permiso que solo permite a administradores ver listas de usuarios,
    pero permite a usuarios ver su propia información en detalle
    """
    
    def has_permission(self, request, view):
        # Solo administradores pueden acceder a listas (GET sin ID específico)
        if view.action == 'list':
            return request.user.is_authenticated and request.user.is_admin
        
        # Para crear usuarios, solo administradores
        if view.action == 'create':
            return request.user.is_authenticated and request.user.is_admin
        
        # Para acciones de detalle (retrieve, update, destroy), verificar en has_object_permission
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Los administradores pueden hacer cualquier cosa
        if request.user.is_admin:
            return True
        
        # Los usuarios solo pueden acceder a su propia información
        return obj == request.user
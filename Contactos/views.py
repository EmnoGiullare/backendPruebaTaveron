from django.shortcuts import get_object_or_404
from django.db.models import Q, Prefetch
from rest_framework import status, filters
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend

from .models import (
    Contacto, TipoRelacion, TipoTelefono, TipoEmail, TipoDireccion,
    TelefonoContacto, EmailContacto, DireccionContacto
)
from .serializers import (
    ContactoSerializer, 
    ContactoCreateUpdateSerializer,
    ContactoListSerializer,
    ContactoListSimpleSerializer,  # Nuevo serializer simple
    TipoRelacionSerializer,
    TipoTelefonoSerializer,
    TipoEmailSerializer,
    TipoDireccionSerializer
)

class ContactoPagination(PageNumberPagination):
    """Paginación personalizada para contactos"""
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 100
    
    def get_paginated_response(self, data):
        return Response({
            'pagination': {
                'count': self.page.paginator.count,
                'next': self.get_next_link(),
                'previous': self.get_previous_link(),
                'page_size': self.page_size,
                'total_pages': self.page.paginator.num_pages,
                'current_page': self.page.number,
            },
            'results': data
        })

class ContactoListCreateView(ListCreateAPIView):
    """
    Vista para listar y crear contactos del usuario autenticado
    GET /contactos/ - Lista paginada de contactos con filtros
    POST /contactos/ - Crear nuevo contacto
    
    Parámetros de consulta opcionales:
    - simple=true : Retorna datos básicos sin teléfonos/emails/direcciones completos
    """
    permission_classes = [IsAuthenticated]
    pagination_class = ContactoPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    # Campos por los que se puede filtrar
    filterset_fields = {
        'tipo_relacion': ['exact', 'in'],
        'favorito': ['exact'],
        'activo': ['exact'],
        'empresa': ['icontains'],
        'cargo': ['icontains'],
        'fecha_nacimiento': ['exact', 'gte', 'lte', 'year', 'month'],
        'created_at': ['exact', 'gte', 'lte', 'date'],
    }
    
    # Campos para búsqueda de texto
    search_fields = [
        'nombre', 'apellido_pat', 'apellido_mat', 
        'empresa', 'cargo', 'notas',
        'telefonos__numero', 'emails__email'
    ]
    
    # Campos para ordenamiento
    ordering_fields = [
        'nombre', 'apellido_pat', 'created_at', 'updated_at',
        'tipo_relacion__nombre', 'empresa', 'favorito'
    ]
    ordering = ['nombre', 'apellido_pat']

    def get_queryset(self):
        """Filtrar contactos solo del usuario autenticado con optimización de consultas"""
        return Contacto.objects.filter(usuario=self.request.user).select_related(
            'tipo_relacion'
        ).prefetch_related(
            # Optimizar carga de datos relacionados
            Prefetch('telefonos', queryset=TelefonoContacto.objects.select_related('tipo')),
            Prefetch('emails', queryset=EmailContacto.objects.select_related('tipo')),
            Prefetch('direcciones', queryset=DireccionContacto.objects.select_related('tipo'))
        )

    def get_serializer_class(self):
        """Usar diferentes serializers según el método y parámetros"""
        if self.request.method == 'GET':
            # Permitir usar serializer simple con parámetro ?simple=true
            simple = self.request.query_params.get('simple', 'false').lower() == 'true'
            return ContactoListSimpleSerializer if simple else ContactoListSerializer
        return ContactoCreateUpdateSerializer

    def perform_create(self, serializer):
        """Asociar automáticamente el contacto con el usuario autenticado"""
        serializer.save(usuario=self.request.user)

class ContactoDetailView(RetrieveUpdateDestroyAPIView):
    """
    Vista para obtener, actualizar y eliminar un contacto específico
    GET /contactos/{id}/ - Detalle completo del contacto
    PUT /contactos/{id}/ - Actualizar contacto completo
    PATCH /contactos/{id}/ - Actualizar contacto parcial
    DELETE /contactos/{id}/ - Eliminar contacto
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Solo contactos del usuario autenticado"""
        return Contacto.objects.filter(usuario=self.request.user).select_related(
            'tipo_relacion'
        ).prefetch_related(
            Prefetch('telefonos', queryset=TelefonoContacto.objects.select_related('tipo')),
            Prefetch('emails', queryset=EmailContacto.objects.select_related('tipo')),
            Prefetch('direcciones', queryset=DireccionContacto.objects.select_related('tipo'))
        )

    def get_serializer_class(self):
        """Usar diferentes serializers según el método"""
        if self.request.method == 'GET':
            return ContactoSerializer
        return ContactoCreateUpdateSerializer

    def perform_update(self, serializer):
        """Verificar permisos antes de actualizar"""
        if serializer.instance.usuario != self.request.user:
            raise PermissionDenied("No tienes permiso para modificar este contacto")
        serializer.save()

    def perform_destroy(self, instance):
        """Verificar permisos antes de eliminar"""
        if instance.usuario != self.request.user:
            raise PermissionDenied("No tienes permiso para eliminar este contacto")
        instance.delete()

class ContactoTodosView(ListAPIView):
    """
    Vista para obtener TODOS los contactos del usuario sin paginación
    GET /contactos/todos/?simple=true (opcional para datos básicos)
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'apellido_pat', 'apellido_mat', 'empresa']
    ordering = ['nombre', 'apellido_pat']

    def get_queryset(self):
        return Contacto.objects.filter(usuario=self.request.user).select_related(
            'tipo_relacion'
        ).prefetch_related(
            Prefetch('telefonos', queryset=TelefonoContacto.objects.select_related('tipo')),
            Prefetch('emails', queryset=EmailContacto.objects.select_related('tipo')),
            Prefetch('direcciones', queryset=DireccionContacto.objects.select_related('tipo'))
        )

    def get_serializer_class(self):
        """Permitir usar serializer simple con parámetro ?simple=true"""
        simple = self.request.query_params.get('simple', 'false').lower() == 'true'
        return ContactoListSimpleSerializer if simple else ContactoListSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        
        return Response({
            'count': queryset.count(),
            'results': serializer.data
        })

class ContactoFavoritosView(ListAPIView):
    """
    Vista para obtener solo los contactos favoritos
    GET /contactos/favoritos/?simple=true (opcional)
    """
    permission_classes = [IsAuthenticated]
    pagination_class = ContactoPagination

    def get_queryset(self):
        return Contacto.objects.filter(
            usuario=self.request.user, 
            favorito=True
        ).select_related('tipo_relacion').prefetch_related(
            Prefetch('telefonos', queryset=TelefonoContacto.objects.select_related('tipo')),
            Prefetch('emails', queryset=EmailContacto.objects.select_related('tipo')),
            Prefetch('direcciones', queryset=DireccionContacto.objects.select_related('tipo'))
        )

    def get_serializer_class(self):
        simple = self.request.query_params.get('simple', 'false').lower() == 'true'
        return ContactoListSimpleSerializer if simple else ContactoListSerializer

class ContactoBuscarView(ListAPIView):
    """
    Vista para búsqueda avanzada con múltiples criterios
    GET /contactos/buscar/?q=texto&tipo=1&favorito=true&empresa=empresa&simple=true
    """
    permission_classes = [IsAuthenticated]
    pagination_class = ContactoPagination

    def get_queryset(self):
        queryset = Contacto.objects.filter(usuario=self.request.user).select_related(
            'tipo_relacion'
        ).prefetch_related(
            Prefetch('telefonos', queryset=TelefonoContacto.objects.select_related('tipo')),
            Prefetch('emails', queryset=EmailContacto.objects.select_related('tipo')),
            Prefetch('direcciones', queryset=DireccionContacto.objects.select_related('tipo'))
        )
        
        # Parámetros de búsqueda
        q = self.request.query_params.get('q', None)
        tipo_relacion = self.request.query_params.get('tipo', None)
        favorito = self.request.query_params.get('favorito', None)
        empresa = self.request.query_params.get('empresa', None)
        activo = self.request.query_params.get('activo', None)
        
        # Aplicar filtros
        if q:
            queryset = queryset.filter(
                Q(nombre__icontains=q) |
                Q(apellido_pat__icontains=q) |
                Q(apellido_mat__icontains=q) |
                Q(empresa__icontains=q) |
                Q(cargo__icontains=q) |
                Q(notas__icontains=q) |
                Q(telefonos__numero__icontains=q) |
                Q(emails__email__icontains=q)
            ).distinct()
        
        if tipo_relacion:
            queryset = queryset.filter(tipo_relacion_id=tipo_relacion)
        
        if favorito is not None:
            queryset = queryset.filter(favorito=favorito.lower() == 'true')
        
        if empresa:
            queryset = queryset.filter(empresa__icontains=empresa)
            
        if activo is not None:
            queryset = queryset.filter(activo=activo.lower() == 'true')
        
        return queryset

    def get_serializer_class(self):
        simple = self.request.query_params.get('simple', 'false').lower() == 'true'
        return ContactoListSimpleSerializer if simple else ContactoListSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'count': queryset.count(),
            'results': serializer.data
        })

class ContactoPorTipoView(APIView):
    """
    Vista para obtener contactos agrupados por tipo de relación
    GET /contactos/por-tipo/?simple=true (opcional)
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tipos_relacion = TipoRelacion.objects.filter(activo=True)
        resultado = {}
        simple = request.query_params.get('simple', 'false').lower() == 'true'
        
        for tipo in tipos_relacion:
            contactos = Contacto.objects.filter(
                usuario=request.user, 
                tipo_relacion=tipo
            ).select_related('tipo_relacion').prefetch_related(
                Prefetch('telefonos', queryset=TelefonoContacto.objects.select_related('tipo')),
                Prefetch('emails', queryset=EmailContacto.objects.select_related('tipo')),
                Prefetch('direcciones', queryset=DireccionContacto.objects.select_related('tipo'))
            )
            
            serializer_class = ContactoListSimpleSerializer if simple else ContactoListSerializer
            serializer = serializer_class(contactos, many=True, context={'request': request})
            
            resultado[tipo.nombre] = {
                'tipo_info': {
                    'id': tipo.id,
                    'nombre': tipo.nombre,
                    'color': tipo.color,
                    'descripcion': tipo.descripcion
                },
                'count': contactos.count(),
                'contactos': serializer.data
            }
        
        return Response(resultado)

class ContactoEstadisticasView(APIView):
    """Vista para obtener estadísticas de contactos del usuario"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = Contacto.objects.filter(usuario=request.user)
        
        estadisticas = {
            'total_contactos': queryset.count(),
            'contactos_favoritos': queryset.filter(favorito=True).count(),
            'contactos_activos': queryset.filter(activo=True).count(),
            'contactos_inactivos': queryset.filter(activo=False).count(),
            'por_tipo_relacion': {},
            'con_telefono': queryset.filter(telefonos__isnull=False).distinct().count(),
            'con_email': queryset.filter(emails__isnull=False).distinct().count(),
            'con_direccion': queryset.filter(direcciones__isnull=False).distinct().count(),
        }
        
        tipos = TipoRelacion.objects.all()
        for tipo in tipos:
            count = queryset.filter(tipo_relacion=tipo).count()
            if count > 0:
                estadisticas['por_tipo_relacion'][tipo.nombre] = {
                    'count': count,
                    'color': tipo.color
                }
        
        return Response(estadisticas)

class ContactoToggleFavoritoView(APIView):
    """Vista para alternar el estado de favorito de un contacto"""
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            contacto = Contacto.objects.get(pk=pk, usuario=request.user)
        except Contacto.DoesNotExist:
            return Response(
                {'error': 'Contacto no encontrado'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        contacto.favorito = not contacto.favorito
        contacto.save()
        
        serializer = ContactoSerializer(contacto, context={'request': request})
        return Response({
            'message': f'Contacto {"agregado a" if contacto.favorito else "removido de"} favoritos',
            'contacto': serializer.data
        })

# Vistas para obtener tipos (sin cambios)
class TipoRelacionListView(ListAPIView):
    """GET /tipos/relacion/ - Lista de tipos de relación activos"""
    queryset = TipoRelacion.objects.filter(activo=True)
    serializer_class = TipoRelacionSerializer
    permission_classes = [IsAuthenticated]

class TipoTelefonoListView(ListAPIView):
    """GET /tipos/telefono/ - Lista de tipos de teléfono"""
    queryset = TipoTelefono.objects.all()
    serializer_class = TipoTelefonoSerializer
    permission_classes = [IsAuthenticated]

class TipoEmailListView(ListAPIView):
    """GET /tipos/email/ - Lista de tipos de email"""
    queryset = TipoEmail.objects.all()
    serializer_class = TipoEmailSerializer
    permission_classes = [IsAuthenticated]

class TipoDireccionListView(ListAPIView):
    """GET /tipos/direccion/ - Lista de tipos de dirección"""
    queryset = TipoDireccion.objects.all()
    serializer_class = TipoDireccionSerializer
    permission_classes = [IsAuthenticated]

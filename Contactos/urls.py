from django.urls import path
from .views import (
    ContactoListCreateView,
    ContactoDetailView,
    ContactoTodosView,
    ContactoFavoritosView,
    ContactoPorTipoView,
    ContactoEstadisticasView,
    ContactoToggleFavoritoView,
    ContactoBuscarView,
    TipoRelacionListView,
    TipoTelefonoListView,
    TipoEmailListView,
    TipoDireccionListView,
)

urlpatterns = [
    # CRUD básico de contactos
    path('', ContactoListCreateView.as_view(), name='contacto-list-create'),
    path('<int:pk>/', ContactoDetailView.as_view(), name='contacto-detail'),
    
    # Endpoints especiales de contactos
    path('todos/', ContactoTodosView.as_view(), name='contacto-todos'),
    path('favoritos/', ContactoFavoritosView.as_view(), name='contacto-favoritos'),
    path('por-tipo/', ContactoPorTipoView.as_view(), name='contacto-por-tipo'),
    path('estadisticas/', ContactoEstadisticasView.as_view(), name='contacto-estadisticas'),
    path('buscar/', ContactoBuscarView.as_view(), name='contacto-buscar'),
    path('<int:pk>/toggle-favorito/', ContactoToggleFavoritoView.as_view(), name='contacto-toggle-favorito'),
    
    # Endpoints para obtener tipos (para formularios)
    path('tipos/relacion/', TipoRelacionListView.as_view(), name='tipo-relacion-list'),
    path('tipos/telefono/', TipoTelefonoListView.as_view(), name='tipo-telefono-list'),
    path('tipos/email/', TipoEmailListView.as_view(), name='tipo-email-list'),
    path('tipos/direccion/', TipoDireccionListView.as_view(), name='tipo-direccion-list'),
]
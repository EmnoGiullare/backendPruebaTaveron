from django.contrib.auth.models import AbstractUser
from django.db import models

# se crea un modelo de usuario personalizado
class CustomUser(AbstractUser):
    """
    CustomUser extiende AbstractUser para agregar campos y funcionalidades personalizadas.
    Atributos:
        rol (CharField): Rol del usuario en el sistema, con opciones predefinidas (Administrador, Usuario, Moderador).
        phone (CharField): Número de teléfono del usuario (opcional).
        address (CharField): Dirección del usuario (opcional).
        created_at (DateTimeField): Fecha y hora de creación del usuario.
        updated_at (DateTimeField): Fecha y hora de la última actualización del usuario.
    Clases anidadas:
        RolChoices (TextChoices): Define las opciones de roles disponibles para el usuario.
    Métodos:
        __str__(): Retorna el email del usuario si está disponible, de lo contrario el username.
        get_full_name(): Retorna el nombre completo del usuario (nombre y apellido).
        is_admin (property): Verifica si el usuario tiene el rol de administrador.
    Meta:
        verbose_name: Nombre singular para el modelo en el admin de Django.
        verbose_name_plural: Nombre plural para el modelo en el admin de Django.
        ordering: Ordena los usuarios por fecha de creación descendente.
    """
    # Choices para seleccionar el rol 
    class RolChoices(models.TextChoices):
        ADMIN = 'admin', 'Administrador'
        USER = 'user', 'Usuario'
        MODERATOR = 'moderator', 'Moderador'
    
    # Campos adicionales personalizados
    rol = models.CharField(
        max_length=50, 
        choices=RolChoices.choices,
        default=RolChoices.USER,
        blank=True, 
        null=True, 
        help_text="Rol del usuario en el sistema"
    )
    phone = models.CharField(max_length=20, blank=True, null=True,
                           help_text="Número de teléfono del usuario")
    address = models.CharField(max_length=255, blank=True, null=True,
                             help_text="Dirección del usuario")
    
    # Campos de control de tiempo
    created_at = models.DateTimeField(auto_now_add=True, 
                                    help_text="Fecha de creación del usuario")
    updated_at = models.DateTimeField(auto_now=True,
                                    help_text="Fecha de última actualización")
    
    # Información adicional del modelo
    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.email if self.email else self.username
    
    def get_full_name(self):
        """Retorna el nombre completo del usuario"""
        return f"{self.first_name} {self.last_name}".strip()
    
    @property
    def is_admin(self):
        """Verifica si el usuario es administrador"""
        return self.rol == self.RolChoices.ADMIN

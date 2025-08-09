from django.db import models
from django.core.validators import RegexValidator
from Usuarios.models import CustomUser

# Modelos para la aplicación de Contactos - Agenda Electrónica
class TipoRelacion(models.Model):
    """
    Modelo para definir los tipos de relación entre el usuario y sus contactos.
    Ejemplos: Familiar, Trabajo, Escuela, Amigos, Negocios, etc.
    """
    nombre = models.CharField(
        max_length=50, 
        unique=True,
        help_text="Nombre del tipo de relación (ej: Familiar, Trabajo, Amigos)"
    )
    descripcion = models.TextField(
        blank=True, 
        null=True,
        help_text="Descripción opcional del tipo de relación"
    )
    color = models.CharField(
        max_length=7, 
        default="#007bff",
        help_text="Color hexadecimal para identificar visualmente el tipo (#RRGGBB)"
    )
    activo = models.BooleanField(
        default=True,
        help_text="Indica si este tipo de relación está disponible para usar"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Tipo de Relación"
        verbose_name_plural = "Tipos de Relación"
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre

class Contacto(models.Model):
    """
    Modelo principal para almacenar información de contactos en la agenda electrónica.
    Cada contacto pertenece a un usuario específico y tiene un tipo de relación.
    """
    # Relación con el usuario propietario
    usuario = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE,
        related_name='contactos',
        help_text="Usuario propietario de este contacto"
    )
    
    # Información básica del contacto
    nombre = models.CharField(
        max_length=100,
        help_text="Nombre del contacto"
    )
    apellido_pat = models.CharField(
        max_length=100,
        blank=True,
        help_text="Apellido paterno del contacto"
    )
    
    apellido_mat = models.CharField(
        max_length=100,
        blank=True,
        help_text="Apellido materno del contacto"
    )
    
    # Relación con tipo de relación
    tipo_relacion = models.ForeignKey(
        TipoRelacion,
        on_delete=models.PROTECT,
        related_name='contactos',
        help_text="Tipo de relación con este contacto"
    )
    
    # --------------- Información adicional
    empresa = models.CharField(
        max_length=150,
        blank=True,
        help_text="Empresa donde trabaja el contacto"
    )
    cargo = models.CharField(
        max_length=100,
        blank=True,
        help_text="Cargo o posición del contacto"
    )
    fecha_nacimiento = models.DateField(
        blank=True,
        null=True,
        help_text="Fecha de nacimiento del contacto"
    )
    notas = models.TextField(
        blank=True,
        help_text="Notas adicionales sobre el contacto"
    )
    
    # ------------------------ Campos de control
    favorito = models.BooleanField(
        default=False,
        help_text="Marca este contacto como favorito"
    )
    activo = models.BooleanField(
        default=True,
        help_text="Indica si este contacto está activo"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Contacto"
        verbose_name_plural = "Contactos"
        ordering = ['nombre', 'apellido_pat']
        unique_together = ['usuario', 'nombre', 'apellido_pat', 'apellido_mat']
    
    def __str__(self):
        return self.nombre_completo
    
    @property
    def nombre_completo(self):
        """Retorna el nombre completo del contacto"""
        nombres = [self.nombre, self.apellido_pat, self.apellido_mat]
        return " ".join([n for n in nombres if n]).strip()
    
    @property
    def iniciales(self):
        """Retorna las iniciales del contacto"""
        iniciales = []
        if self.nombre:
            iniciales.append(self.nombre[0].upper())
        if self.apellido_pat:
            iniciales.append(self.apellido_pat[0].upper())
        return "".join(iniciales)


class TipoTelefono(models.Model):
    """
    Tipos de teléfono: Móvil, Casa, Trabajo, Fax, etc.
    """
    nombre = models.CharField(
        max_length=30,
        unique=True,
        help_text="Tipo de teléfono (ej: Móvil, Casa, Trabajo)"
    )
    icono = models.CharField(
        max_length=50,
        blank=True,
        help_text="Nombre del icono para mostrar en la interfaz"
    )
    
    class Meta:
        verbose_name = "Tipo de Teléfono"
        verbose_name_plural = "Tipos de Teléfono"
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre

class TelefonoContacto(models.Model):
    """
    Modelo para almacenar múltiples teléfonos por contacto.
    Un contacto puede tener varios números con diferentes tipos.
    """
    contacto = models.ForeignKey(
        Contacto,
        on_delete=models.CASCADE,
        related_name='telefonos',
        help_text="Contacto al que pertenece este teléfono"
    )
    tipo = models.ForeignKey(
        TipoTelefono,
        on_delete=models.PROTECT,
        help_text="Tipo de teléfono"
    )
    numero = models.CharField(
        max_length=20,
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message="El número debe tener entre 9 y 15 dígitos. Puede incluir el símbolo '+'."
        )],
        help_text="Número de teléfono"
    )
    principal = models.BooleanField(
        default=False,
        help_text="Marca este teléfono como principal para el contacto"
    )
    activo = models.BooleanField(
        default=True,
        help_text="Indica si este teléfono está activo"
    )
    
    class Meta:
        verbose_name = "Teléfono de Contacto"
        verbose_name_plural = "Teléfonos de Contacto"
        unique_together = ['contacto', 'numero']
    
    def __str__(self):
        return f"{self.contacto.nombre_completo} - {self.tipo.nombre}: {self.numero}"

class TipoEmail(models.Model):
    """
    Tipos de email: Personal, Trabajo, Académico, etc.
    """
    nombre = models.CharField(
        max_length=30,
        unique=True,
        help_text="Tipo de email (ej: Personal, Trabajo, Académico)"
    )
    icono = models.CharField(
        max_length=50,
        blank=True,
        help_text="Nombre del icono para mostrar en la interfaz"
    )
    
    class Meta:
        verbose_name = "Tipo de Email"
        verbose_name_plural = "Tipos de Email"
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre

class EmailContacto(models.Model):
    """
    Modelo para almacenar múltiples emails por contacto.
    Un contacto puede tener varios emails con diferentes tipos.
    """
    contacto = models.ForeignKey(
        Contacto,
        on_delete=models.CASCADE,
        related_name='emails',
        help_text="Contacto al que pertenece este email"
    )
    tipo = models.ForeignKey(
        TipoEmail,
        on_delete=models.PROTECT,
        help_text="Tipo de email"
    )
    email = models.EmailField(
        help_text="Dirección de email"
    )
    principal = models.BooleanField(
        default=False,
        help_text="Marca este email como principal para el contacto"
    )
    activo = models.BooleanField(
        default=True,
        help_text="Indica si este email está activo"
    )
    
    class Meta:
        verbose_name = "Email de Contacto"
        verbose_name_plural = "Emails de Contacto"
        unique_together = ['contacto', 'email']
    
    def __str__(self):
        return f"{self.contacto.nombre_completo} - {self.tipo.nombre}: {self.email}"


class TipoDireccion(models.Model):
    """
    Tipos de dirección: Casa, Trabajo, Temporal, etc.
    """
    nombre = models.CharField(
        max_length=30,
        unique=True,
        help_text="Tipo de dirección (ej: Casa, Trabajo, Temporal)"
    )
    icono = models.CharField(
        max_length=50,
        blank=True,
        help_text="Nombre del icono para mostrar en la interfaz"
    )
    
    class Meta:
        verbose_name = "Tipo de Dirección"
        verbose_name_plural = "Tipos de Dirección"
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre

class DireccionContacto(models.Model):
    """
    Modelo para almacenar múltiples direcciones por contacto.
    Un contacto puede tener varias direcciones con diferentes tipos.
    """
    contacto = models.ForeignKey(
        Contacto,
        on_delete=models.CASCADE,
        related_name='direcciones',
        help_text="Contacto al que pertenece esta dirección"
    )
    tipo = models.ForeignKey(
        TipoDireccion,
        on_delete=models.PROTECT,
        help_text="Tipo de dirección"
    )
    calle = models.CharField(
        max_length=200,
        help_text="Calle y número"
    )
    ciudad = models.CharField(
        max_length=100,
        help_text="Ciudad"
    )
    estado_provincia = models.CharField(
        max_length=100,
        help_text="Estado o provincia"
    )
    codigo_postal = models.CharField(
        max_length=20,
        help_text="Código postal"
    )
    pais = models.CharField(
        max_length=100,
        default="México",
        help_text="País"
    )
    principal = models.BooleanField(
        default=False,
        help_text="Marca esta dirección como principal para el contacto"
    )
    activo = models.BooleanField(
        default=True,
        help_text="Indica si esta dirección está activa"
    )
    
    class Meta:
        verbose_name = "Dirección de Contacto"
        verbose_name_plural = "Direcciones de Contacto"
    
    def __str__(self):
        return f"{self.contacto.nombre_completo} - {self.tipo.nombre}: {self.calle}, {self.ciudad}"
    
    @property
    def direccion_completa(self):
        """Retorna la dirección completa formateada"""
        partes = [
            self.calle,
            self.ciudad,
            self.estado_provincia,
            self.codigo_postal,
            self.pais
        ]
        return ", ".join([p for p in partes if p]).strip()

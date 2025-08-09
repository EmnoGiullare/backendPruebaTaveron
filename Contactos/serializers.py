from rest_framework import serializers
from .models import (
    Contacto, TipoRelacion, TelefonoContacto, EmailContacto, 
    DireccionContacto, TipoTelefono, TipoEmail, TipoDireccion
)

class TipoRelacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoRelacion
        fields = ['id', 'nombre', 'descripcion', 'color']

class TipoTelefonoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoTelefono
        fields = ['id', 'nombre', 'icono']

class TipoEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoEmail
        fields = ['id', 'nombre', 'icono']

class TipoDireccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoDireccion
        fields = ['id', 'nombre', 'icono']

class TelefonoContactoSerializer(serializers.ModelSerializer):
    tipo = TipoTelefonoSerializer(read_only=True)
    tipo_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = TelefonoContacto
        fields = ['id', 'tipo', 'tipo_id', 'numero', 'principal', 'activo']

class EmailContactoSerializer(serializers.ModelSerializer):
    tipo = TipoEmailSerializer(read_only=True)
    tipo_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = EmailContacto
        fields = ['id', 'tipo', 'tipo_id', 'email', 'principal', 'activo']

class DireccionContactoSerializer(serializers.ModelSerializer):
    tipo = TipoDireccionSerializer(read_only=True)
    tipo_id = serializers.IntegerField(write_only=True)
    direccion_completa = serializers.ReadOnlyField()
    
    class Meta:
        model = DireccionContacto
        fields = [
            'id', 'tipo', 'tipo_id', 'calle', 'ciudad', 'estado_provincia',
            'codigo_postal', 'pais', 'principal', 'activo', 'direccion_completa'
        ]

class ContactoListSerializer(serializers.ModelSerializer):
    """Serializer para listados que incluye todos los teléfonos, emails y direcciones"""
    tipo_relacion = TipoRelacionSerializer(read_only=True)
    nombre_completo = serializers.ReadOnlyField()
    iniciales = serializers.ReadOnlyField()
    
    # Incluir todos los teléfonos, emails y direcciones
    telefonos = TelefonoContactoSerializer(many=True, read_only=True)
    emails = EmailContactoSerializer(many=True, read_only=True)
    direcciones = DireccionContactoSerializer(many=True, read_only=True)
    
    # Mantener los campos principales para compatibilidad
    telefono_principal = serializers.SerializerMethodField()
    email_principal = serializers.SerializerMethodField()
    direccion_principal = serializers.SerializerMethodField()
    
    class Meta:
        model = Contacto
        fields = [
            'id', 'nombre', 'apellido_pat', 'apellido_mat', 'nombre_completo',
            'iniciales', 'tipo_relacion', 'empresa', 'cargo', 'favorito',
            'activo', 'fecha_nacimiento', 'notas',
            # Listados completos
            'telefonos', 'emails', 'direcciones',
            # Campos principales para referencia rápida
            'telefono_principal', 'email_principal', 'direccion_principal',
            'created_at', 'updated_at'
        ]
    
    def get_telefono_principal(self, obj):
        """Retorna solo el número del teléfono principal"""
        telefono = obj.telefonos.filter(principal=True).first()
        return telefono.numero if telefono else None
    
    def get_email_principal(self, obj):
        """Retorna solo el email principal"""
        email = obj.emails.filter(principal=True).first()
        return email.email if email else None
    
    def get_direccion_principal(self, obj):
        """Retorna la dirección principal completa"""
        direccion = obj.direcciones.filter(principal=True).first()
        return direccion.direccion_completa if direccion else None

class ContactoListSimpleSerializer(serializers.ModelSerializer):
    """Serializer simplificado para cuando solo necesitas datos básicos (opcional)"""
    tipo_relacion = TipoRelacionSerializer(read_only=True)
    nombre_completo = serializers.ReadOnlyField()
    iniciales = serializers.ReadOnlyField()
    telefono_principal = serializers.SerializerMethodField()
    email_principal = serializers.SerializerMethodField()
    
    class Meta:
        model = Contacto
        fields = [
            'id', 'nombre', 'apellido_pat', 'apellido_mat', 'nombre_completo',
            'iniciales', 'tipo_relacion', 'empresa', 'cargo', 'favorito',
            'activo', 'telefono_principal', 'email_principal', 'created_at'
        ]
    
    def get_telefono_principal(self, obj):
        telefono = obj.telefonos.filter(principal=True).first()
        return telefono.numero if telefono else None
    
    def get_email_principal(self, obj):
        email = obj.emails.filter(principal=True).first()
        return email.email if email else None

class ContactoSerializer(serializers.ModelSerializer):
    """Serializer completo para detalles de contacto (sin cambios)"""
    tipo_relacion = TipoRelacionSerializer(read_only=True)
    telefonos = TelefonoContactoSerializer(many=True, read_only=True)
    emails = EmailContactoSerializer(many=True, read_only=True)
    direcciones = DireccionContactoSerializer(many=True, read_only=True)
    nombre_completo = serializers.ReadOnlyField()
    iniciales = serializers.ReadOnlyField()
    usuario_info = serializers.SerializerMethodField()
    
    class Meta:
        model = Contacto
        fields = [
            'id', 'nombre', 'apellido_pat', 'apellido_mat', 'nombre_completo',
            'iniciales', 'tipo_relacion', 'empresa', 'cargo', 'fecha_nacimiento',
            'notas', 'favorito', 'activo', 'telefonos', 'emails', 'direcciones',
            'usuario_info', 'created_at', 'updated_at'
        ]
    
    def get_usuario_info(self, obj):
        return {
            'id': obj.usuario.id,
            'nombre': obj.usuario.get_full_name(),
            'email': obj.usuario.email
        }

class ContactoCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer para crear y actualizar contactos (sin cambios)"""
    telefonos = TelefonoContactoSerializer(many=True, required=False)
    emails = EmailContactoSerializer(many=True, required=False)
    direcciones = DireccionContactoSerializer(many=True, required=False)
    
    class Meta:
        model = Contacto
        fields = [
            'nombre', 'apellido_pat', 'apellido_mat', 'tipo_relacion',
            'empresa', 'cargo', 'fecha_nacimiento', 'notas', 'favorito',
            'activo', 'telefonos', 'emails', 'direcciones'
        ]
    
    def create(self, validated_data):
        telefonos_data = validated_data.pop('telefonos', [])
        emails_data = validated_data.pop('emails', [])
        direcciones_data = validated_data.pop('direcciones', [])
        
        contacto = Contacto.objects.create(**validated_data)
        
        # Crear teléfonos
        for telefono_data in telefonos_data:
            TelefonoContacto.objects.create(contacto=contacto, **telefono_data)
        
        # Crear emails
        for email_data in emails_data:
            EmailContacto.objects.create(contacto=contacto, **email_data)
        
        # Crear direcciones
        for direccion_data in direcciones_data:
            DireccionContacto.objects.create(contacto=contacto, **direccion_data)
        
        return contacto
    
    def update(self, instance, validated_data):
        telefonos_data = validated_data.pop('telefonos', [])
        emails_data = validated_data.pop('emails', [])
        direcciones_data = validated_data.pop('direcciones', [])
        
        # Actualizar campos del contacto
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Actualizar teléfonos (estrategia: eliminar y recrear)
        if telefonos_data:
            instance.telefonos.all().delete()
            for telefono_data in telefonos_data:
                TelefonoContacto.objects.create(contacto=instance, **telefono_data)
        
        # Actualizar emails
        if emails_data:
            instance.emails.all().delete()
            for email_data in emails_data:
                EmailContacto.objects.create(contacto=instance, **email_data)
        
        # Actualizar direcciones
        if direcciones_data:
            instance.direcciones.all().delete()
            for direccion_data in direcciones_data:
                DireccionContacto.objects.create(contacto=instance, **direccion_data)
        
        return instance
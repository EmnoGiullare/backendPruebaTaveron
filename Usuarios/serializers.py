from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import serializers
from .models import CustomUser

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Serializador personalizado para obtener pares de tokens JWT con información adicional del usuario.
    Este serializador extiende el `TokenObtainPairSerializer` por defecto para incluir reclamaciones extra
    en el token JWT y datos adicionales del usuario en la respuesta.
    Métodos
    -------
    get_token(cls, user):
        Devuelve un token con reclamaciones personalizadas: nombre completo del usuario, correo electrónico y estado de staff.
    validate(self, attrs):
        Valida y retorna los datos del token, agregando un diccionario 'user' con detalles del usuario
        (id, nombre de usuario, correo electrónico, nombre, apellido) a la respuesta.
    """
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Agregar reclamaciones personalizadas al token
        token['name'] = user.get_full_name()
        token['email'] = user.email
        token['is_staff'] = user.is_staff
        token['rol'] = user.rol  # Agregar el rol personalizado

        return token

    # sobreescribe el método validate para agregar información del usuario a la respuesta
    def validate(self, attrs):
        data = super().validate(attrs)

        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'rol': self.user.rol,
            'phone': self.user.phone,
            'address': self.user.address,
        }
        return data

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer para mostrar información básica del usuario
    """
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'full_name',
                 'rol', 'phone', 'address', 'created_at', 'updated_at', 'is_active', 'last_login']
        read_only_fields = ['id', 'created_at', 'updated_at', 'last_login']

class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para crear nuevos usuarios (solo administradores)
    """
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'password_confirm', 
                 'first_name', 'last_name', 'rol', 'phone', 'address']

    def validate_email(self, value):
        """
        Validar que el email sea único
        """
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("Ya existe un usuario con este email.")
        return value

    def validate_username(self, value):
        """
        Validar que el username sea único
        """
        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError("Ya existe un usuario con este nombre de usuario.")
        return value

    def validate(self, attrs):
        """
        Validar que las contraseñas coincidan
        """
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Las contraseñas no coinciden.")
        return attrs

    def create(self, validated_data):
        """
        Crear usuario con contraseña encriptada
        """
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = CustomUser.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user

class UserRegisterSerializer(serializers.ModelSerializer):
    """
    Serializer para registro público de usuarios (sin autenticación requerida)
    El rol siempre será 'user' por defecto
    """
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'password_confirm', 
                 'first_name', 'last_name', 'phone', 'address']

    def validate_email(self, value):
        """
        Validar que el email sea único
        """
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("Ya existe un usuario con este email.")
        return value

    def validate_username(self, value):
        """
        Validar que el username sea único
        """
        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError("Ya existe un usuario con este nombre de usuario.")
        return value

    def validate_password(self, value):
        """
        Validaciones adicionales para la contraseña
        """
        if len(value) < 8:
            raise serializers.ValidationError("La contraseña debe tener al menos 8 caracteres.")
        return value

    def validate(self, attrs):
        """
        Validar que las contraseñas coincidan
        """
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Las contraseñas no coinciden.")
        return attrs

    def create(self, validated_data):
        """
        Crear usuario con rol 'user' por defecto y contraseña encriptada
        """
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        # Asegurar que el rol siempre sea 'user' para registros públicos
        validated_data['rol'] = CustomUser.RolChoices.USER
        
        user = CustomUser.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user

class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer para actualizar usuarios (sin contraseña)
    """
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 
                 'rol', 'phone', 'address', 'is_active']

    def validate_email(self, value):
        """
        Validar que el email sea único (excluyendo el usuario actual)
        """
        user = self.instance
        if CustomUser.objects.filter(email=value).exclude(pk=user.pk).exists():
            raise serializers.ValidationError("Ya existe un usuario con este email.")
        return value

    def validate_username(self, value):
        """
        Validar que el username sea único (excluyendo el usuario actual)
        """
        user = self.instance
        if CustomUser.objects.filter(username=value).exclude(pk=user.pk).exists():
            raise serializers.ValidationError("Ya existe un usuario con este nombre de usuario.")
        return value

class PasswordChangeSerializer(serializers.Serializer):
    """
    Serializer para cambiar contraseña
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)
    new_password_confirm = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("Las nuevas contraseñas no coinciden.")
        return attrs

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("La contraseña actual es incorrecta.")
        return value

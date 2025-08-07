from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

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

        # Add extra responses here
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'rol': self.user.rol,  # Incluir el rol en la respuesta
            'phone': self.user.phone,
            'address': self.user.address,
        }
        return data

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

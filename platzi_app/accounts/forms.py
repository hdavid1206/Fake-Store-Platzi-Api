from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re

class CustomUserRegistrationForm(UserCreationForm):
    """
    Formulario personalizado para el registro de usuarios
    con campos adicionales y validaciones mejoradas
    """
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Tu nombre',
            'autocomplete': 'given-name'
        }),
        label='Nombre'
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Tu apellido',
            'autocomplete': 'family-name'
        }),
        label='Apellido'
    )
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'tu@email.com',
            'autocomplete': 'email'
        }),
        label='Correo Electrónico'
    )
    
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre de usuario único',
            'autocomplete': 'username'
        }),
        label='Nombre de Usuario',
        help_text='Debe tener entre 3 y 150 caracteres. Solo letras, números y @/./+/-/_ permitidos.'
    )
    
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Mínimo 8 caracteres',
            'autocomplete': 'new-password'
        }),
        label='Contraseña',
        help_text='Debe tener al menos 8 caracteres y no puede ser solo numérica.'
    )
    
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Repite tu contraseña',
            'autocomplete': 'new-password'
        }),
        label='Confirmar Contraseña',
        help_text='Ingresa la misma contraseña para verificación.'
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']

    def clean_username(self):
        """
        Validación personalizada para el nombre de usuario
        """
        username = self.cleaned_data.get('username')
        
        if not username:
            raise ValidationError('El nombre de usuario es requerido.')
        
        # Verificar longitud mínima
        if len(username) < 3:
            raise ValidationError('El nombre de usuario debe tener al menos 3 caracteres.')
        
        # Verificar caracteres permitidos
        if not re.match(r'^[\w.@+-]+$', username):
            raise ValidationError('El nombre de usuario solo puede contener letras, números y @/./+/-/_')
        
        # Verificar que no comience o termine con puntos
        if username.startswith('.') or username.endswith('.'):
            raise ValidationError('El nombre de usuario no puede comenzar o terminar con un punto.')
        
        # Verificar disponibilidad
        if User.objects.filter(username=username).exists():
            raise ValidationError('Este nombre de usuario ya está en uso.')
        
        return username

    def clean_email(self):
        """
        Validación personalizada para el email
        """
        email = self.cleaned_data.get('email')
        
        if not email:
            raise ValidationError('El correo electrónico es requerido.')
        
        # Verificar que el email no esté ya registrado
        if User.objects.filter(email=email).exists():
            raise ValidationError('Ya existe una cuenta con este correo electrónico.')
        
        # Validación adicional del formato de email
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise ValidationError('Por favor ingresa un correo electrónico válido.')
        
        return email.lower()  # Convertir a minúsculas

    def clean_first_name(self):
        """
        Validación para el nombre
        """
        first_name = self.cleaned_data.get('first_name', '').strip()
        
        if not first_name:
            raise ValidationError('El nombre es requerido.')
        
        if len(first_name) < 2:
            raise ValidationError('El nombre debe tener al menos 2 caracteres.')
        
        # Solo permitir letras y espacios
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s]+$', first_name):
            raise ValidationError('El nombre solo puede contener letras y espacios.')
        
        return first_name.title()  # Capitalizar primera letra

    def clean_last_name(self):
        """
        Validación para el apellido
        """
        last_name = self.cleaned_data.get('last_name', '').strip()
        
        if not last_name:
            raise ValidationError('El apellido es requerido.')
        
        if len(last_name) < 2:
            raise ValidationError('El apellido debe tener al menos 2 caracteres.')
        
        # Solo permitir letras y espacios
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s]+$', last_name):
            raise ValidationError('El apellido solo puede contener letras y espacios.')
        
        return last_name.title()  # Capitalizar primera letra

    def clean_password1(self):
        """
        Validación personalizada para la contraseña
        """
        password1 = self.cleaned_data.get('password1')
        
        if not password1:
            raise ValidationError('La contraseña es requerida.')
        
        # Verificar longitud mínima
        if len(password1) < 8:
            raise ValidationError('La contraseña debe tener al menos 8 caracteres.')
        
        # Verificar que no sea solo numérica
        if password1.isdigit():
            raise ValidationError('La contraseña no puede ser solo numérica.')
        
        # Verificar que no sea muy común
        common_passwords = [
            'password', '12345678', 'qwerty', 'abc123', 
            'password123', '123456789', 'letmein'
        ]
        if password1.lower() in common_passwords:
            raise ValidationError('Esta contraseña es demasiado común.')
        
        return password1

    def clean(self):
        """
        Validación general del formulario
        """
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')

        # Verificar que las contraseñas coincidan
        if password1 and password2 and password1 != password2:
            raise ValidationError({
                'password2': 'Las contraseñas no coinciden.'
            })

        # Verificar que la contraseña no contenga el username o email
        if password1 and username:
            if username.lower() in password1.lower():
                raise ValidationError({
                    'password1': 'La contraseña no puede contener el nombre de usuario.'
                })

        if password1 and email:
            email_local = email.split('@')[0]
            if email_local.lower() in password1.lower():
                raise ValidationError({
                    'password1': 'La contraseña no puede contener partes de tu correo electrónico.'
                })

        return cleaned_data

    def save(self, commit=True):
        """
        Guardar el usuario con los datos adicionales
        """
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
        
        return user


class CustomAuthenticationForm(AuthenticationForm):
    """
    Formulario personalizado para el inicio de sesión
    """
    username = forms.CharField(
        max_length=254,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre de usuario o email',
            'autocomplete': 'username',
            'autofocus': True
        }),
        label='Usuario'
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Tu contraseña',
            'autocomplete': 'current-password'
        }),
        label='Contraseña'
    )

    error_messages = {
        'invalid_login': 'Por favor ingresa un usuario y contraseña correctos. '
                        'Ten en cuenta que ambos campos pueden ser sensibles a mayúsculas.',
        'inactive': 'Esta cuenta está inactiva.',
    }

    def clean_username(self):
        """
        Limpiar y validar el campo username
        """
        username = self.cleaned_data.get('username')
        
        if not username:
            raise ValidationError('El nombre de usuario es requerido.')
        
        # Permitir login tanto con username como con email
        return username.strip()

    def clean(self):
        """
        Validación personalizada del formulario de login
        """
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username is not None and password:
            # Intentar autenticar con username normal primero
            self.user_cache = self.authenticate(
                username=username,
                password=password,
            )
            
            # Si no funciona y parece un email, intentar encontrar el usuario por email
            if self.user_cache is None and '@' in username:
                try:
                    user = User.objects.get(email=username)
                    self.user_cache = self.authenticate(
                        username=user.username,
                        password=password,
                    )
                except User.DoesNotExist:
                    pass

            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data

    def authenticate(self, username=None, password=None):
        """
        Método de autenticación personalizado
        """
        from django.contrib.auth import authenticate
        return authenticate(self.request, username=username, password=password)
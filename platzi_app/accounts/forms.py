from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
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
        
        if len(username) < 3:
            raise ValidationError('El nombre de usuario debe tener al menos 3 caracteres.')
        
        if User.objects.filter(username=username).exists():
            raise ValidationError('Este nombre de usuario ya está en uso.')
        
        if not re.match(r'^[a-zA-Z0-9@.+_-]+$', username):
            raise ValidationError('Nombre de usuario inválido. Solo letras, números y @/./+/-/_ permitidos.')
        
        return username.strip()

    def clean_email(self):
        """
        Validación personalizada para el correo electrónico
        """
        email = self.cleaned_data.get('email')
        
        if User.objects.filter(email=email).exists():
            raise ValidationError('Este correo electrónico ya está registrado.')
        
        return email

    def clean_password1(self):
        """
        Validación personalizada para la contraseña
        """
        password = self.cleaned_data.get('password1')
        
        if len(password) < 8:
            raise ValidationError('La contraseña debe tener al menos 8 caracteres.')
        
        if password.isnumeric():
            raise ValidationError('La contraseña no puede ser completamente numérica.')
        
        return password

    def clean(self):
        """
        Validación general del formulario
        """
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        
        if password1 and password2 and password1 != password2:
            raise ValidationError('Las contraseñas no coinciden.')
        
        return cleaned_data

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
        
        return username.strip()

    def clean(self):
        """
        Validación personalizada del formulario de login
        """
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username is not None and password:
            # Intentar autenticar con username normal primero
            self.user_cache = authenticate(
                self.request,
                username=username,
                password=password,
            )
            
            # Si no funciona y parece un email, intentar encontrar el usuario por email
            if self.user_cache is None and '@' in username:
                try:
                    user = User.objects.get(email=username)
                    self.user_cache = authenticate(
                        self.request,
                        username=user.username,
                        password=password,
                    )
                except User.DoesNotExist:
                    pass

            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)

        return cleaned_data
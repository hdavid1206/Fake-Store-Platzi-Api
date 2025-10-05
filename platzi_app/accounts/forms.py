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
        label='Nombre',
        error_messages={'required': 'Este campo es obligatorio.'}
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Tu apellido',
            'autocomplete': 'family-name'
        }),
        label='Apellido',
        error_messages={'required': 'Este campo es obligatorio.'}
    )
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'tu@email.com',
            'autocomplete': 'email'
        }),
        label='Correo Electrónico',
        error_messages={
            'required': 'Este campo es obligatorio.',
            'invalid': 'Por favor, introduce una dirección de correo electrónico válida.',
            'unique': 'Este correo electrónico ya está registrado.',
        }
    )
    
    
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Mínimo 8 caracteres',
            'autocomplete': 'new-password'
        }),
        label='Contraseña',
        help_text='Debe tener al menos 8 caracteres y no puede ser solo numérica.',
        error_messages={'required': 'Este campo es obligatorio.'}
    )

    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Repite tu contraseña',
            'autocomplete': 'new-password'
        }),
        label='Confirmar Contraseña',
        help_text='Ingresa la misma contraseña para verificación.',
        error_messages={'required': 'Este campo es obligatorio.'}
    )

    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Elige un nombre de usuario',
            'autocomplete': 'username'
        }),
        label='Nombre de usuario',
        help_text='Requerido. 150 caracteres o menos. Letras, dígitos y @/./+/-/_ solamente.',
        error_messages={'required': 'Este campo es obligatorio.'}
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def clean_email(self):
        """
        Validación personalizada para el correo electrónico
        """
        email = self.cleaned_data.get('email')
        
        if User.objects.filter(email=email).exists():
            raise ValidationError('Este correo electrónico ya está registrado.')
        
        return email

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

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
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
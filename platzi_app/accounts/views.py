from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.views import LoginView
from .forms import CustomUserRegistrationForm, CustomAuthenticationForm
from django.contrib.auth.decorators import login_required
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from .serializers import UserRegistrationSerializer, UserLoginSerializer, UserSerializer

# VISTAS HTML (para interfaz web)
def register_view(request):
    """
    Vista para registro de usuarios (HTML)
    """
    if request.user.is_authenticated:
        return redirect('fake_store_api:inicio')
    
    if request.method == 'POST':
        form = CustomUserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(
                request, 
                f'¡Bienvenido {user.first_name}! Tu cuenta ha sido creada exitosamente. '
                'Ya puedes iniciar sesión.'
            )
            return redirect('accounts:login')
        else:
            messages.error(
                request,
                'Hay errores en el formulario. Por favor corrígelos e intenta nuevamente.'
            )
    else:
        form = CustomUserRegistrationForm()

    context = {
        'form': form,
        'title': 'Crear Cuenta - Harold Tienda'
    }
    return render(request, 'accounts/register.html', context)

def login_view(request):
    """
    Vista para login de usuarios (HTML)
    """
    if request.user.is_authenticated:
        return redirect('fake_store_api:inicio')
    
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(
                    request,
                    f'¡Bienvenido de nuevo, {user.first_name or user.username}!'
                )
                
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect('fake_store_api:inicio')
        else:
            messages.error(
                request,
                'Credenciales incorrectas. Por favor verifica tu usuario y contraseña.'
            )
    else:
        form = CustomAuthenticationForm()

    context = {
        'form': form,
        'title': 'Iniciar Sesión - Harold Tienda',
        'next': request.GET.get('next', '')
    }
    return render(request, 'accounts/login.html', context)

def logout_view(request):
    """
    Vista para logout de usuarios (HTML)
    """
    if request.user.is_authenticated:
        user_name = request.user.first_name or request.user.username
        logout(request)
        messages.success(request, f'¡Hasta luego, {user_name}! Has cerrado sesión exitosamente.')
    
    return redirect('fake_store_api:inicio')

@login_required
def inicio(request):
    """
    Vista de inicio para usuarios autenticados
    """
    user_name = request.user.first_name or request.user.username
    context = {
        'user_name': user_name,
        'title': 'Inicio - Harold Tienda'
    }
    return render(request, 'accounts/inicio.html', context)

# VISTAS API (para endpoints REST)
@api_view(['POST'])
@permission_classes([AllowAny])
def register_api(request):
    """
    Endpoint para registro de usuarios via API
    """
    serializer = UserRegistrationSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'success': True,
            'message': 'Usuario registrado exitosamente',
            'user': UserSerializer(user).data,
            'token': token.key
        }, status=status.HTTP_201_CREATED)
    
    return Response({
        'success': False,
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_api(request):
    """
    Endpoint para login de usuarios via API
    """
    serializer = UserLoginSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'success': True,
            'message': 'Login exitoso',
            'user': UserSerializer(user).data,
            'token': token.key
        }, status=status.HTTP_200_OK)
    
    return Response({
        'success': False,
        'errors': serializer.errors
    }, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_api(request):
    """
    Endpoint para logout de usuarios via API
    """
    try:
        request.user.auth_token.delete()
        return Response({
            'success': True,
            'message': 'Sesión cerrada exitosamente'
        }, status=status.HTTP_200_OK)
    except:
        return Response({
            'success': True,
            'message': 'Sesión cerrada'
        }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile_api(request):
    """
    Endpoint para obtener el perfil del usuario autenticado
    """
    serializer = UserSerializer(request.user)
    return Response({
        'success': True,
        'user': serializer.data
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([AllowAny])
def check_username_api(request):
    """
    Endpoint para verificar disponibilidad de nombre de usuario
    """
    username = request.GET.get('username', '').strip()
    
    if not username:
        return Response({
            'success': False,
            'error': 'Parámetro username requerido'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    exists = User.objects.filter(username__iexact=username).exists()
    
    return Response({
        'success': True,
        'available': not exists,
        'username': username
    }, status=status.HTTP_200_OK)
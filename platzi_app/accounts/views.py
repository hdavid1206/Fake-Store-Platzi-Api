# Agregar estas importaciones al inicio del archivo accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.views import LoginView
from .forms import CustomUserRegistrationForm, CustomAuthenticationForm

# Agregar estas vistas al final del archivo accounts/views.py

class CustomRegisterView(CreateView):
    """
    Vista basada en clase para el registro de usuarios
    """
    form_class = CustomUserRegistrationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:login')

    def form_valid(self, form):
        """
        Procesar formulario válido
        """
        response = super().form_valid(form)
        user = form.save()
        
        messages.success(
            self.request, 
            f'¡Bienvenido {user.first_name}! Tu cuenta ha sido creada exitosamente. '
            'Ya puedes iniciar sesión.'
        )
        
        return response

    def form_invalid(self, form):
        """
        Procesar formulario inválido
        """
        messages.error(
            self.request,
            'Hay errores en el formulario. Por favor corrígelos e intenta nuevamente.'
        )
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        """
        Agregar contexto adicional
        """
        context = super().get_context_data(**kwargs)
        context['title'] = 'Crear Cuenta - Harold Tienda'
        return context


class CustomLoginView(LoginView):
    """
    Vista basada en clase para el inicio de sesión
    """
    form_class = CustomAuthenticationForm
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        """
        URL de redirección después del login exitoso
        """
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return reverse_lazy('fake_store_api:inicio')

    def form_valid(self, form):
        """
        Procesar login exitoso
        """
        response = super().form_valid(form)
        user = form.get_user()
        
        messages.success(
            self.request,
            f'¡Bienvenido de nuevo, {user.first_name or user.username}!'
        )
        
        return response

    def form_invalid(self, form):
        """
        Procesar login fallido
        """
        messages.error(
            self.request,
            'Credenciales incorrectas. Por favor verifica tu usuario y contraseña.'
        )
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        """
        Agregar contexto adicional
        """
        context = super().get_context_data(**kwargs)
        context['title'] = 'Iniciar Sesión - Harold Tienda'
        return context


def register_view(request):
    """
    Vista basada en función para el registro (alternativa)
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
    Vista basada en función para el login (alternativa)
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
                
                next_url = request.GET.get('next', 'fake_store_api:inicio')
                return redirect(next_url)
        else:
            messages.error(
                request,
                'Credenciales incorrectas. Por favor verifica tu usuario y contraseña.'
            )
    else:
        form = CustomAuthenticationForm()

    context = {
        'form': form,
        'title': 'Iniciar Sesión - Harold Tienda'
    }
    return render(request, 'accounts/login.html', context)


def logout_view(request):
    """
    Vista para cerrar sesión
    """
    if request.user.is_authenticated:
        user_name = request.user.first_name or request.user.username
        logout(request)
        messages.success(request, f'¡Hasta luego, {user_name}! Has cerrado sesión exitosamente.')
    
    return redirect('fake_store_api:inicio')
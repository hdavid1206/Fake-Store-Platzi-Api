from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.views import LoginView
from .forms import CustomUserRegistrationForm, CustomAuthenticationForm
from django.contrib.auth.decorators import login_required

class CustomRegisterView(CreateView):
    form_class = CustomUserRegistrationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:login')

    def form_valid(self, form):
        response = super().form_valid(form)
        user = form.save()
        messages.success(
            self.request, 
            f'¡Bienvenido {user.first_name}! Tu cuenta ha sido creada exitosamente. '
            'Ya puedes iniciar sesión.'
        )
        return response

    def form_invalid(self, form):
        messages.error(
            self.request,
            'Hay errores en el formulario. Por favor corrígelos e intenta nuevamente.'
        )
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Crear Cuenta - Harold Tienda'
        return context

class CustomLoginView(LoginView):
    form_class = CustomAuthenticationForm
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return reverse_lazy('fake_store_api:inicio')

    def form_valid(self, form):
        response = super().form_valid(form)
        user = form.get_user()
        messages.success(
            self.request,
            f'¡Bienvenido de nuevo, {user.first_name or user.username}!'
        )
        return response

    def form_invalid(self, form):
        messages.error(
            self.request,
            'Credenciales incorrectas. Por favor verifica tu usuario y contraseña.'
        )
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Iniciar Sesión - Harold Tienda'
        return context

def register_view(request):
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
                
                # Redirigir a la página que intentaban acceder O al inicio
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
        'next': request.GET.get('next', '')  # Pasar el parámetro next al template
    }
    return render(request, 'accounts/login.html', context)

def logout_view(request):
    if request.user.is_authenticated:
        user_name = request.user.first_name or request.user.username
        logout(request)
        messages.success(request, f'¡Hasta luego, {user_name}! Has cerrado sesión exitosamente.')
    
    return redirect('fake_store_api:inicio')

@login_required
def inicio(request):
    """
    Vista de inicio para usuarios autenticados en la app accounts.
    Muestra un dashboard personalizado para el usuario.
    """
    user_name = request.user.first_name or request.user.username
    context = {
        'user_name': user_name,
        'title': 'Inicio - Harold Tienda'
    }
    return render(request, 'accounts/inicio.html', context)
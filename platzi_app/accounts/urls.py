from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # URLs de las vistas de templates (agregar estas líneas)
    path('register/', views.CustomRegisterView.as_view(), name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Alternativas con vistas basadas en funciones (opcional)
    # path('register/', views.register_view, name='register'),
    # path('login/', views.login_view, name='login'),
    
    # URLs de la API de autenticación (mantener las existentes)
    path('api/register/', views.register_api, name='api_register'),
    path('api/login/', views.login_api, name='api_login'),
    path('api/logout/', views.logout_api, name='api_logout'),
    path('api/profile/', views.user_profile_api, name='api_profile'),
    path('api/check-username/', views.check_username_api, name='api_check_username'),
]
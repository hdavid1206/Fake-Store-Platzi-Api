from django.urls import path
from . import views

app_name = 'accounts'

<<<<<<< HEAD
urlpatterns = [ 
=======
urlpatterns = [
    # URLs de vistas HTML (existentes)
>>>>>>> 728a6c6339d15b5b757aef8f85219a31b0e0d16e
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # ✅ NUEVAS URLs API (las que necesitas)
    path('api/register/', views.register_api, name='api_register'),
    path('api/login/', views.login_api, name='api_login'),
    path('api/logout/', views.logout_api, name='api_logout'),
    path('api/profile/', views.user_profile_api, name='api_profile'),
    path('api/check-username/', views.check_username_api, name='api_check_username'),
]
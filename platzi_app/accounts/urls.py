from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('', views.inicio, name='inicio'),  # Esta línea causa el error
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
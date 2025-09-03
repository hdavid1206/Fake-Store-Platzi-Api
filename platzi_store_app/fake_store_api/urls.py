from django.urls import path
from . import views
app_name = 'fake_store_api'
urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('obtener-productos/', views.obtener_productos, name='obtener_productos'),
    path('agregar-producto/', views.agregar_producto, name='agregar_producto'),
    path('agregar-producto-api/', views.agregar_producto_api, name='agregar_producto_api'),
]
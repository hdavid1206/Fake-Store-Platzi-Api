# fake_store_api/urls.py - RUTAS CORRECTAS
from django.urls import path
from . import views

app_name = 'fake_store_api'

urlpatterns = [
    # VISTAS PÚBLICAS
    path('', views.inicio, name='inicio'),
    path('obtener_productos/', views.obtener_productos, name='obtener_productos'),
    
    # VISTAS PROTEGIDAS (requieren login)
    path('agregar_producto/', views.agregar_producto, name='agregar_producto'),
    path('agregar_producto_api/', views.agregar_producto_api, name='agregar_producto_api'),
    path('editar_producto/', views.editar_producto, name='editar_producto'),
    path('editar_producto/<int:producto_id>/', views.editar_producto, name='editar_producto_con_id'),
    path('editar_producto_api/', views.editar_producto_api, name='editar_producto_api'),
    path('eliminar_producto/<int:producto_id>/', views.eliminar_producto, name='eliminar_producto'),
    
    # ✅ CARRITO PROTEGIDO (aquí es donde deben estar)
    path('cart/', views.view_cart, name='cart'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove_from_cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('update_cart_quantity/<int:product_id>/', views.update_cart_quantity, name='update_cart_quantity'),
]
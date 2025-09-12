from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import requests
from django.http import JsonResponse
from django.contrib import messages
import json
from .forms import AgregarProductoForm

# VISTAS PÚBLICAS (accesibles sin login)
def inicio(request):
    return render(request, 'inicio.html')

def obtener_productos(request):
    if request.method == 'GET':
        try:
            consulta_productos = request.GET.get('obtener_productos', 'todos')
            url = "https://api.escuelajs.co/api/v1"
            
            all_products = []
            page = 1
            while True:
                response = requests.get(f"{url}/products", params={'page': page, 'limit': 100}, timeout=20)
                response.raise_for_status()
                data = response.json()
                all_products.extend(data)
                if len(data) < 100:
                    break
                page += 1
            
            categories_response = requests.get(f"{url}/categories", timeout=20)
            categories = categories_response.json() if categories_response.status_code == 200 else []
            
            resultado = {
                'data': all_products,
                'total': len(all_products),
                'categories': categories
            }
            
            contexto = {
                'success': True,
                'total_mostrados': resultado['total'],
                'consulta': 'Todos los productos',
                'mensaje': f'Mostrando {resultado["total"]} productos',
                'productos': resultado['data'],
                'categorias': resultado['categories'],
            }
            
            return render(request, 'obtener_producto.html', contexto)

        except requests.exceptions.RequestException as e:
            contexto = {
                'success': False,
                'error_message': f'Error al conectar con la API: {e}'
            }
            return render(request, 'obtener_producto.html', contexto, status=500)

    return JsonResponse({'error': 'Solo se permiten solicitudes GET'}, status=405)

# VISTAS PROTEGIDAS (requieren login)
@login_required
def agregar_producto(request):
    form = AgregarProductoForm()
    contexto = {'form': form}
    return render(request, 'agregar_producto.html', contexto)

@login_required
def agregar_producto_api(request):
    if request.method == 'POST':
        form = AgregarProductoForm(request.POST)
        if form.is_valid():
            try:
                data = {
                    'title': form.cleaned_data['titulo'],
                    'price': form.cleaned_data['precio'],
                    'description': form.cleaned_data['descripcion'],
                    'categoryId': form.cleaned_data['categoria'],
                    'images': form.get_images_list()
                }
                
                response = requests.post("https://api.escuelajs.co/api/v1/products/", json=data, timeout=20)
                response.raise_for_status()
                producto = response.json()
                
                messages.success(request, '¡Producto agregado exitosamente!')
                return redirect('fake_store_api:obtener_productos')
            except requests.exceptions.RequestException as e:
                messages.error(request, f'Error al conectar con la API: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    
    contexto = {'form': form}
    return render(request, 'agregar_producto.html', contexto)

@login_required
def editar_producto(request, producto_id=None):
    if producto_id is None:
        return redirect('fake_store_api:obtener_productos')
    
    try:
        response = requests.get(f"https://api.escuelajs.co/api/v1/products/{producto_id}", timeout=20)
        response.raise_for_status()
        producto_data = response.json()
    except requests.exceptions.RequestException:
        messages.error(request, 'Error al obtener el producto.')
        return redirect('fake_store_api:obtener_productos')
    
    form = AgregarProductoForm(initial={
        'titulo': producto_data.get('title'),
        'precio': producto_data.get('price'),
        'descripcion': producto_data.get('description'),
        'categoria': producto_data.get('category', {}).get('id'),
        'imagen1': producto_data.get('images', [''])[0] if producto_data.get('images') else ''
    })
    
    contexto = {
        'form': form,
        'producto_id': producto_id,
        'producto_data': producto_data,
        'es_edicion': True
    }
    return render(request, 'editar_producto.html', contexto)

@login_required
def editar_producto_api(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Solo POST'}, status=405)
    
    producto_id = request.POST.get('id')
    if not producto_id:
        messages.error(request, 'ID del producto requerido.')
        return redirect('fake_store_api:editar_producto')
    
    form = AgregarProductoForm(request.POST)
    if form.is_valid():
        try:
            data = {
                'title': form.cleaned_data['titulo'],
                'price': form.cleaned_data['precio'],
                'description': form.cleaned_data['descripcion'],
                'categoryId': form.cleaned_data['categoria'],
                'images': form.get_images_list()
            }
            
            response = requests.put(f"https://api.escuelajs.co/api/v1/products/{producto_id}", json=data, timeout=20)
            response.raise_for_status()
            
            messages.success(request, '¡Producto actualizado exitosamente!')
            return redirect('fake_store_api:obtener_productos')
        except requests.exceptions.RequestException as e:
            messages.error(request, f'Error al conectar con la API: {str(e)}')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, f'{field}: {error}')
    
    contexto = {
        'form': form,
        'producto_id': producto_id,
        'es_edicion': True
    }
    return render(request, 'editar_producto.html', contexto)

@login_required
def eliminar_producto(request, producto_id=None):
    if request.method != 'POST':
        return JsonResponse({'error': 'Solo se permiten solicitudes POST'}, status=405)

    if not producto_id:
        try:
            json_data = json.loads(request.body)
            producto_id = json_data.get('id')
        except json.JSONDecodeError:
            pass
    
    if not producto_id:
        return JsonResponse({'error': 'ID del producto requerido'}, status=400)

    try:
        response = requests.delete(f"https://api.escuelajs.co/api/v1/products/{producto_id}", timeout=20)
        
        if response.status_code == 200:
            return JsonResponse({'success': True, 'message': '¡Producto eliminado exitosamente!'}, status=200)
        elif response.status_code == 404:
            return JsonResponse({'error': 'Producto no encontrado'}, status=404)
        else:
            return JsonResponse({'error': f'Error al eliminar: {response.status_code}'}, status=response.status_code)
    except requests.exceptions.RequestException as e:
        return JsonResponse({'error': str(e)}, status=500)

# VISTAS DE CARRITO PROTEGIDAS
@login_required
def add_to_cart(request, product_id):
    cart = request.session.get('cart', {})
    
    if str(product_id) not in cart:
        try:
            response = requests.get(f"https://api.escuelajs.co/api/v1/products/{product_id}")
            response.raise_for_status()
            product = response.json()
            cart[str(product_id)] = {
                'title': product['title'],
                'price': product['price'],
                'quantity': 1,
                'image': product['images'][0] if product['images'] else ''
            }
        except requests.exceptions.RequestException:
            messages.error(request, 'Error al obtener el producto.')
            return redirect('fake_store_api:obtener_productos')
    else:
        cart[str(product_id)]['quantity'] += 1
    
    request.session['cart'] = cart
    messages.success(request, 'Producto agregado al carrito.')
    return redirect('fake_store_api:obtener_productos')

@login_required
def view_cart(request):
    cart = request.session.get('cart', {})
    total = sum(item['price'] * item['quantity'] for item in cart.values())
    contexto = {'cart': cart, 'total': total}
    return render(request, 'cart.html', contexto)

@login_required
def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    if str(product_id) in cart:
        del cart[str(product_id)]
    request.session['cart'] = cart
    messages.success(request, 'Producto removido del carrito.')
    return redirect('fake_store_api:cart')

@login_required
def update_cart_quantity(request, product_id):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        cart = request.session.get('cart', {})
        if str(product_id) in cart and quantity > 0:
            cart[str(product_id)]['quantity'] = quantity
        request.session['cart'] = cart
    return redirect('fake_store_api:cart')
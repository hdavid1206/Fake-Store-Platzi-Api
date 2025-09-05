from django.shortcuts import render, redirect
import requests
from django.http import JsonResponse
from django.contrib import messages
import json
from .forms import AgregarProductoForm

def inicio(request):
    return render(request, 'inicio.html')

def obtener_productos(request):
    if request.method == 'GET':
        try:
            consulta_productos = request.GET.get('obtener_productos', 'todos')
            url = "https://api.escuelajs.co/api/v1"
            
            # Obtener productos con paginación mejorada
            all_products = []
            page = 1
            while True:
                response = requests.get(f"{url}/products", params={'page': page, 'limit': 100}, timeout=20)
                response.raise_for_status()
                data = response.json()
                all_products.extend(data)
                if len(data) < 100:  # Si devuelve menos de 100, es la última página
                    break
                page += 1
            
            # Obtener categorías
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

def agregar_producto(request):
    form = AgregarProductoForm()
    contexto = {'form': form}
    return render(request, 'agregar_producto.html', contexto)

def agregar_producto_api(request):
    if request.method == 'POST':
        form = AgregarProductoForm(request.POST)

        if form.is_valid():
            try:
                # Extraer datos del formulario
                titulo = form.cleaned_data['titulo']
                precio = float(form.cleaned_data['precio'])
                descripcion = form.cleaned_data['descripcion']
                categoria_id = int(form.cleaned_data['categoria'])

                # Obtener lista de imágenes
                imagenes = form.get_images_list()

                # Preparar datos para la API
                url = "https://api.escuelajs.co/api/v1"
                datos = {
                    "title": titulo,
                    "price": precio,
                    "description": descripcion,
                    "categoryId": categoria_id,
                    "images": imagenes
                }

                # Hacer petición POST
                response = requests.post(f"{url}/products", json=datos, timeout=20)

                if response.status_code == 201:
                    resultado = response.json()
                    messages.success(request, f'¡Producto "{resultado.get("title", titulo)}" agregado exitosamente!')
                    return redirect('fake_store_api:obtener_productos')

                elif response.status_code == 400:
                    # Mostrar detalles del error de la API
                    try:
                        error_detail = response.json()
                        messages.error(request, f'Error en los datos enviados: {error_detail}')
                    except:
                        messages.error(request, 'Error al agregar el producto: Datos inválidos.')
                else:
                    messages.error(request, f'Error al agregar el producto. Código de estado: {response.status_code}')

            except requests.exceptions.Timeout:
                messages.error(request, 'Tiempo de espera agotado. El servidor tardó demasiado en responder.')
                
            except requests.exceptions.ConnectionError:
                messages.error(request, 'No se pudo conectar con el servidor. Verifica tu conexión a internet.')
                
            except requests.exceptions.RequestException as e:
                messages.error(request, f'Error de red: {str(e)}')
                
            except ValueError as e:
                messages.error(request, f'Error en los datos: {str(e)}')
                
            except json.JSONDecodeError:
                messages.error(request, 'Error al procesar la respuesta del servidor.')
                
            except Exception as e:
                messages.error(request, f'Error inesperado: {str(e)}')
        else:
            # Si el formulario no es válido, mostrar errores específicos
            messages.error(request, "Corrige los siguientes errores:")
            for field, errors in form.errors.items():
                field_label = form.fields[field].label or field
                for error in errors:
                    messages.error(request, f"• {field_label}: {error}")
    
    # En caso de error o método incorrecto, se mantiene en la misma página con el formulario y los mensajes de error
    return render(request, 'agregar_producto.html', {'form': form})

def editar_producto(request):
    """Vista mejorada para editar productos"""
    # Obtener el ID del producto desde GET o POST
    producto_id = request.GET.get('id') or request.POST.get('product_id')
    
    # Inicializar el formulario
    form = AgregarProductoForm()
    producto_data = None
    
    # Si se proporciona un ID, intentar obtener los datos del producto
    if producto_id:
        try:
            url = "https://api.escuelajs.co/api/v1"
            response = requests.get(f"{url}/products/{producto_id}", timeout=20)
            
            if response.status_code == 200:
                producto_data = response.json()
                
                # Pre-llenar el formulario con los datos existentes
                initial_data = {
                    'titulo': producto_data.get('title', ''),
                    'precio': producto_data.get('price', ''),
                    'descripcion': producto_data.get('description', ''),
                    'categoria': producto_data.get('category', {}).get('id', ''),
                    'imagen1': producto_data.get('images', [''])[0] if producto_data.get('images') else ''
                }
                
                # Si hay datos del POST (errores de validación), usar esos
                if request.method == 'POST':
                    form = AgregarProductoForm(request.POST)
                else:
                    form = AgregarProductoForm(initial=initial_data)
                    
            elif response.status_code == 404:
                messages.error(request, 'Producto no encontrado.')
            else:
                messages.error(request, f'Error al obtener el producto: {response.status_code}')
                
        except requests.exceptions.RequestException as e:
            messages.error(request, f'Error de conexión: {str(e)}')
    
    # Si no hay datos del producto pero hay datos en POST (desde JavaScript)
    elif request.method == 'POST':
        initial_data = {
            'titulo': request.POST.get('product_title', ''),
            'precio': request.POST.get('product_price', ''),
            'descripcion': request.POST.get('product_description', ''),
            'categoria': request.POST.get('product_category', ''),
            'imagen1': request.POST.get('product_image', '')
        }
        form = AgregarProductoForm(initial=initial_data)
        producto_id = request.POST.get('product_id')
    
    contexto = {
        'form': form,
        'producto_id': producto_id,
        'producto_data': producto_data,
        'es_edicion': bool(producto_id)
    }
    
    return render(request, 'editar_producto.html', contexto)

def editar_producto_api(request):
    """API para actualizar productos con validación mejorada"""
    if request.method == 'POST':
        form = AgregarProductoForm(request.POST)
        producto_id = request.POST.get('id') or request.POST.get('product_id')
        
        if not producto_id:
            messages.error(request, 'ID del producto requerido para editar.')
            contexto = {
                'form': form,
                'es_edicion': False
            }
            return render(request, 'editar_producto.html', contexto)

        if form.is_valid():
            try:
                # Extraer datos del formulario
                titulo = form.cleaned_data['titulo']
                precio = float(form.cleaned_data['precio'])
                descripcion = form.cleaned_data['descripcion']
                categoria_id = int(form.cleaned_data['categoria'])

                # Obtener lista de imágenes
                imagenes = form.get_images_list()

                # Verificar que la categoría existe antes de enviar
                url = "https://api.escuelajs.co/api/v1"
                
                # Validar categoría
                try:
                    cat_response = requests.get(f"{url}/categories/{categoria_id}", timeout=10)
                    if cat_response.status_code != 200:
                        messages.error(request, f'La categoría con ID {categoria_id} no existe en el servidor.')
                        contexto = {
                            'form': form,
                            'producto_id': producto_id,
                            'es_edicion': True
                        }
                        return render(request, 'editar_producto.html', contexto)
                except requests.RequestException:
                    messages.error(request, 'Error al validar la categoría. Intenta más tarde.')
                    contexto = {
                        'form': form,
                        'producto_id': producto_id,
                        'es_edicion': True
                    }
                    return render(request, 'editar_producto.html', contexto)

                # Preparar datos para la API
                datos = {
                    "title": titulo,
                    "price": precio,
                    "description": descripcion,
                    "categoryId": categoria_id,
                    "images": imagenes
                }

                # Hacer petición PUT
                response = requests.put(f"{url}/products/{producto_id}", json=datos, timeout=20)
                
                # Debug: mostrar la respuesta para entender el error
                if response.status_code != 200:
                    try:
                        error_detail = response.json()
                        messages.error(request, f'Error del servidor: {error_detail}')
                    except:
                        messages.error(request, f'Error del servidor (código {response.status_code}): {response.text[:200]}')

                if response.status_code == 200:
                    resultado = response.json()
                    messages.success(request, f'¡Producto "{resultado.get("title", titulo)}" actualizado exitosamente!')    
                    return redirect('fake_store_api:obtener_productos')

                elif response.status_code == 404:
                    messages.error(request, 'Producto no encontrado en el servidor.')
                elif response.status_code == 400:
                    messages.error(request, 'Error al actualizar el producto: Los datos enviados no son válidos.')
                else:
                    messages.error(request, f'Error al actualizar el producto. Código de estado: {response.status_code}')

            except requests.exceptions.Timeout:
                messages.error(request, 'Tiempo de espera agotado. El servidor tardó demasiado en responder.')
                
            except requests.exceptions.ConnectionError:
                messages.error(request, 'No se pudo conectar con el servidor. Verifica tu conexión a internet.')
                
            except requests.exceptions.RequestException as e:
                messages.error(request, f'Error de red: {str(e)}')
                
            except ValueError as e:
                messages.error(request, f'Error en los datos: {str(e)}')
                
            except json.JSONDecodeError:
                messages.error(request, 'Error al procesar la respuesta del servidor.')
                
            except Exception as e:
                messages.error(request, f'Error inesperado: {str(e)}')
        else:
            # Si el formulario no es válido, mostrar errores específicos
            messages.error(request, "Hay errores en el formulario:")
            for field, errors in form.errors.items():
                field_label = form.fields[field].label or field
                for error in errors:
                    messages.error(request, f"• {field_label}: {error}")
    
    # En caso de error o método incorrecto, se mantiene en la página de edición
    contexto = {
        'form': form,
        'producto_id': producto_id,
        'es_edicion': True
    }
    return render(request, 'editar_producto.html', contexto)

def eliminar_producto(request, producto_id=None):
    """API mejorada para eliminar productos"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Solo se permiten solicitudes POST'}, status=405)

    # Obtener ID del producto desde diferentes fuentes
    if not producto_id:
        producto_id = request.POST.get('id')
    
    # Si no está en POST form data, verificar en JSON body
    if not producto_id:
        try:
            json_data = json.loads(request.body)
            producto_id = json_data.get('id')
        except (json.JSONDecodeError, AttributeError):
            pass
    
    if not producto_id:
        return JsonResponse({'error': 'ID del producto requerido'}, status=400)

    try:
        # Hacer petición DELETE a la API externa
        response = requests.delete(f"https://api.escuelajs.co/api/v1/products/{producto_id}", timeout=20)
        
        if response.status_code == 200:
            return JsonResponse({
                'success': True, 
                'message': '¡Producto eliminado exitosamente!'
            }, status=200)
        
        elif response.status_code == 404:
            return JsonResponse({'error': 'Producto no encontrado'}, status=404)
        else:
            return JsonResponse({
                'error': f'Error al eliminar el producto. Código de estado: {response.status_code}'
            }, status=response.status_code)

    except requests.exceptions.Timeout:
        return JsonResponse({
            'error': 'Tiempo de espera agotado. El servidor tardó demasiado en responder.'
        }, status=500)
        
    except requests.exceptions.ConnectionError:
        return JsonResponse({
            'error': 'No se pudo conectar con el servidor. Verifica tu conexión a internet.'
        }, status=500)
        
    except requests.exceptions.RequestException as e:
        return JsonResponse({'error': f'Error de red: {str(e)}'}, status=500)
        
    except Exception as e:
        return JsonResponse({'error': f'Error inesperado: {str(e)}'}, status=500)
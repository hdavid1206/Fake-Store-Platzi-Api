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
            
            # Realizamos la petición a la API
            response = requests.get(f"{url}/products", timeout=20)
            response.raise_for_status()
            
            if response.status_code == 200:
                resultado = response.json()
                
                # Limitamos a los primeros 15 productos
                if isinstance(resultado, list) and len(resultado) >= 15:
                    primeros_15 = resultado[:15]
                else:
                    primeros_15 = resultado if isinstance(resultado, list) else []
                
                contexto = {
                    'success': True,
                    'total_mostrados': len(primeros_15),
                    'consulta': 'Productos disponibles',
                    'productos': primeros_15,
                    'mensaje': f'Mostrando {len(primeros_15)} productos'
                }
                return render(request, 'obtener_producto.html', contexto)
            else:
                contexto = {
                    'success': False,
                    'mensaje': 'No se pudieron obtener los productos'
                }
                return render(request, 'obtener_producto.html', contexto)
                
        except requests.exceptions.Timeout:
            contexto = {
                'success': False,
                'mensaje': 'Tiempo de espera agotado. Inténtalo de nuevo.'
            }
            return render(request, 'obtener_producto.html', contexto)
            
        except requests.exceptions.ConnectionError:
            contexto = {
                'success': False,
                'mensaje': 'Error de conexión con el servidor.'
            }
            return render(request, 'obtener_producto.html', contexto)
            
        except requests.exceptions.RequestException as e:
            contexto = {
                'success': False,
                'mensaje': f'Error al consultar productos: {str(e)}'
            }
            return render(request, 'obtener_producto.html', contexto)
            
        except json.JSONDecodeError:
            contexto = {
                'success': False,
                'mensaje': 'Error al procesar la respuesta del servidor.'
            }
            return render(request, 'obtener_producto.html', contexto)
            
        except Exception as e:
            contexto = {
                'success': False,
                'mensaje': f'Error inesperado: {str(e)}'
            }
            return render(request, 'obtener_producto.html', contexto)
    
    return redirect('fake_store_api:inicio')
    
def agregar_producto(request):
    form = AgregarProductoForm()
    return render(request, 'agregar_producto.html', {'form': form})

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
                    
                    contexto = {
                        'form': AgregarProductoForm(),  # Formulario limpio
                        'success': True,
                        'producto': resultado,
                        'mensaje': f'¡Producto "{resultado.get("title", titulo)}" agregado exitosamente!',
                        'show_success_modal': True
                    }
                    return render(request, 'agregar_producto.html', contexto)
                    
                elif response.status_code == 400:
                    error_data = response.json() if response.content else {}
                    messages.error(request, f'Datos inválidos: {error_data.get("message", "Verifica los campos del formulario")}')
                    
                else:
                    messages.error(request, f'Error del servidor: Código {response.status_code}')
                    
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
            error_messages = []
            for field, errors in form.errors.items():
                field_label = form.fields[field].label or field
                for error in errors:
                    error_messages.append(f"{field_label}: {error}")
            
            if error_messages:
                messages.error(request, "Corrige los siguientes errores:")
                for msg in error_messages:
                    messages.error(request, f"• {msg}")
    
    # En caso de error o método incorrecto
    return render(request, 'agregar_producto.html', {'form': form})
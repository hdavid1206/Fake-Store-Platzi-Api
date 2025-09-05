from django import forms 
import requests

class AgregarProductoForm(forms.Form):
    # Obtener categorías dinámicamente
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            # Intentar obtener categorías de la API
            response = requests.get("https://api.escuelajs.co/api/v1/categories", timeout=10)
            if response.status_code == 200:
                categorias = response.json()
                # Filtrar categorías válidas (que tengan ID numérico válido)
                valid_categories = []
                for cat in categorias[:15]:  # Limitar a 15
                    if isinstance(cat.get('id'), int) and cat.get('name'):
                        valid_categories.append((cat['id'], cat['name']))
                
                if valid_categories:
                    self.fields['categoria'].choices = valid_categories
                else:
                    # Categorías por defecto si no hay válidas
                    self.fields['categoria'].choices = self._get_default_categories()
            else:
                self.fields['categoria'].choices = self._get_default_categories()
        except:
            # Categorías por defecto en caso de error
            self.fields['categoria'].choices = self._get_default_categories()

    def _get_default_categories(self):
        """Retorna categorías por defecto que son válidas en la API"""
        return [
            (1, 'Clothes'),
            (2, 'Electronics'),
            (3, 'Furniture'),
            (4, 'Shoes'),
            (5, 'Others')
        ]

    titulo = forms.CharField(
        max_length=100, 
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingresa el título del producto',
            'id': 'titulo'
        }),
        label='Título del Producto'
    )
    
    precio = forms.FloatField(
        required=True,
        min_value=0.01,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '0.00',
            'step': '0.01',
            'min': '0.01',
            'id': 'precio'
        }),
        label='Precio (USD)'
    )
    
    descripcion = forms.CharField(
        max_length=500, 
        required=True,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Describe detalladamente el producto...',
            'rows': 4,
            'id': 'descripcion'
        }),
        label='Descripción del Producto'
    )
    
    categoria = forms.ChoiceField(
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'categoria'
        }),
        label='Categoría'
    )
    
    imagen1 = forms.URLField(
        required=True,
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'https://ejemplo.com/imagen1.jpg',
            'id': 'imagen1'
        }),
        label='URL Imagen Principal'
    )

    def clean_precio(self):
        precio = self.cleaned_data['precio']
        if precio <= 0:
            raise forms.ValidationError("El precio debe ser mayor a 0")
        if precio > 999999:
            raise forms.ValidationError("El precio no puede ser mayor a $999,999")
        return precio

    def clean_titulo(self):
        titulo = self.cleaned_data['titulo'].strip()
        if len(titulo) < 3:
            raise forms.ValidationError("El título debe tener al menos 3 caracteres")
        return titulo

    def clean_descripcion(self):
        descripcion = self.cleaned_data['descripcion'].strip()
        if len(descripcion) < 10:
            raise forms.ValidationError("La descripción debe tener al menos 10 caracteres")
        return descripcion

    def clean_categoria(self):
        """Validar que la categoría sea válida para la API"""
        categoria_id = self.cleaned_data['categoria']
        
        # Verificar que sea un número entero válido
        try:
            categoria_id = int(categoria_id)
            if categoria_id <= 0:
                raise forms.ValidationError("Selecciona una categoría válida")
        except (ValueError, TypeError):
            raise forms.ValidationError("Selecciona una categoría válida")
            
        # Verificar que la categoría existe en la API
        try:
            response = requests.get(f"https://api.escuelajs.co/api/v1/categories/{categoria_id}", timeout=5)
            if response.status_code != 200:
                raise forms.ValidationError("La categoría seleccionada no existe")
        except requests.RequestException:
            # Si hay error de conexión, permitir categorías por defecto
            if categoria_id not in [1, 2, 3, 4, 5]:
                raise forms.ValidationError("Selecciona una categoría válida")
        
        return categoria_id
        
        # Validar que la URL sea accesible
        try:
            response = requests.head(imagen, timeout=5)
            if response.status_code >= 400:
                raise forms.ValidationError("La URL de la imagen no es accesible")
        except requests.RequestException:
            pass  # No bloquear por problemas de conexión
            
        return imagen

    def clean(self):
        """Validación general del formulario"""
        cleaned_data = super().clean()
        
        # Validar que al menos una imagen sea proporcionada
        imagen1 = cleaned_data.get('imagen1')
        if not imagen1:
            raise forms.ValidationError("Se requiere al menos una imagen del producto")
            
        return cleaned_data

    def get_images_list(self):
        """Retorna lista de imágenes no vacías"""
        images = []
        if self.cleaned_data.get('imagen1'):
            images.append(self.cleaned_data['imagen1'])
        return images

        // Variables globales
        let formValid = false;
        
        // Inicialización cuando carga la página
        document.addEventListener('DOMContentLoaded', function() {
            initializeForm();
            
                document.getElementById('successModal').style.display = 'flex';
            
        });
        
        function initializeForm() {
            const form = document.getElementById('productForm');
            const inputs = form.querySelectorAll('input, select, textarea');
            
            // Agregar event listeners a todos los campos
            inputs.forEach(input => {
                input.addEventListener('input', validateField);
                input.addEventListener('blur', validateField);
                input.addEventListener('change', updateProgress);
            });
            
            // Contadores de caracteres
            setupCharacterCounters();
            
            // Validación inicial
            validateForm();
        }
        
        function setupCharacterCounters() {
            const titulo = document.getElementById('titulo');
            const descripcion = document.getElementById('descripcion');
            
            titulo.addEventListener('input', function() {
                updateCounter('titulo-counter', this.value.length, 100);
            });
            
            descripcion.addEventListener('input', function() {
                updateCounter('descripcion-counter', this.value.length, 500);
            });
        }
        
        function updateCounter(counterId, current, max) {
            const counter = document.getElementById(counterId);
            counter.textContent = current;
            
            if (current > max * 0.8) {
                counter.style.color = '#f59e0b';
            } else if (current > max * 0.9) {
                counter.style.color = '#ef4444';
            } else {
                counter.style.color = '#10b981';
            }
        }
        
        function validateField(event) {
            const field = event.target;
            const fieldName = field.name;
            const value = field.value.trim();
            const errorElement = document.getElementById(fieldName + '-error');
            
            let isValid = true;
            let errorMessage = '';
            
            // Validaciones específicas por campo
            switch(fieldName) {
                case 'titulo':
                    if (!value) {
                        errorMessage = 'El título es requerido';
                        isValid = false;
                    } else if (value.length < 3) {
                        errorMessage = 'El título debe tener al menos 3 caracteres';
                        isValid = false;
                    } else if (value.length > 100) {
                        errorMessage = 'El título no puede exceder 100 caracteres';
                        isValid = false;
                    }
                    break;
                    
                case 'precio':
                    const precio = parseFloat(value);
                    if (!value) {
                        errorMessage = 'El precio es requerido';
                        isValid = false;
                    } else if (isNaN(precio) || precio <= 0) {
                        errorMessage = 'Ingresa un precio válido mayor a 0';
                        isValid = false;
                    } else if (precio > 999999) {
                        errorMessage = 'El precio no puede ser mayor a $999,999';
                        isValid = false;
                    }
                    break;
                    
                case 'descripcion':
                    if (!value) {
                        errorMessage = 'La descripción es requerida';
                        isValid = false;
                    } else if (value.length < 10) {
                        errorMessage = 'La descripción debe tener al menos 10 caracteres';
                        isValid = false;
                    } else if (value.length > 500) {
                        errorMessage = 'La descripción no puede exceder 500 caracteres';
                        isValid = false;
                    }
                    break;
                    
                case 'categoria':
                    if (!value) {
                        errorMessage = 'Selecciona una categoría';
                        isValid = false;
                    }
                    break;
                    
                case 'imagen1':
                    if (!value) {
                        errorMessage = 'La imagen principal es requerida';
                        isValid = false;
                    } else if (!isValidImageUrl(value)) {
                        errorMessage = 'Ingresa una URL de imagen válida (.jpg, .png, .gif, etc.)';
                        isValid = false;
                    }
                    break;
                    
                case 'imagen2':
                case 'imagen3':
                    if (value && !isValidImageUrl(value)) {
                        errorMessage = 'Ingresa una URL de imagen válida (.jpg, .png, .gif, etc.)';
                        isValid = false;
                    }
                    break;
            }
            
            // Mostrar/ocultar error
            if (errorElement) {
                errorElement.textContent = errorMessage;
                errorElement.style.display = errorMessage ? 'block' : 'none';
            }
            
            // Aplicar estilos visuales
            if (isValid) {
                field.classList.remove('error');
                field.classList.add('valid');
            } else {
                field.classList.remove('valid');
                field.classList.add('error');
            }
            
            validateForm();
        }
        
        function isValidImageUrl(url) {
            const imageExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg'];
            return imageExtensions.some(ext => url.toLowerCase().includes(ext));
        }
        
        function validateForm() {
            const requiredFields = ['titulo', 'precio', 'descripcion', 'categoria', 'imagen1'];
            let allValid = true;
            
            requiredFields.forEach(fieldName => {
                const field = document.getElementById(fieldName);
                if (!field || !field.value.trim() || field.classList.contains('error')) {
                    allValid = false;
                }
            });
            
            const submitBtn = document.getElementById('submitBtn');
            submitBtn.disabled = !allValid;
            formValid = allValid;
        }
        
        function updateProgress() {
            const fields = ['titulo', 'precio', 'descripcion', 'categoria', 'imagen1', 'imagen2', 'imagen3'];
            let completed = 0;
            
            fields.forEach(fieldName => {
                const field = document.getElementById(fieldName);
                if (field && field.value.trim() && !field.classList.contains('error')) {
                    completed++;
                }
            });
            
            const percentage = Math.round((completed / fields.length) * 100);
            const progressFill = document.getElementById('progressFill');
            const progressText = document.getElementById('progressText');
            
            progressFill.style.width = percentage + '%';
            progressText.textContent = percentage + '% Completado';
        }
        
        function previewImage(fieldName) {
            const input = document.getElementById(fieldName);
            const preview = document.getElementById('preview-' + fieldName);
            const url = input.value.trim();
            
            if (url && isValidImageUrl(url)) {
                preview.innerHTML = `
                    <img src="${url}" alt="Vista previa" 
                        onload="this.style.display='block'" 
                        onerror="this.parentElement.innerHTML='<p>Error al cargar la imagen</p>'"
                        style="display:none;">
                `;
                preview.style.display = 'block';
            } else {
                preview.innerHTML = '';
                preview.style.display = 'none';
            }
        }
        
        function closeModal() {
            document.getElementById('successModal').style.display = 'none';
        }
        
        // Envío del formulario con loading
        document.getElementById('productForm').addEventListener('submit', function(e) {
            if (!formValid) {
                e.preventDefault();
                return false;
            }
            
            const submitBtn = document.getElementById('submitBtn');
            const btnText = submitBtn.querySelector('.btn-text');
            const btnLoading = submitBtn.querySelector('.btn-loading');
            
            submitBtn.disabled = true;
            btnText.style.display = 'none';
            btnLoading.style.display = 'inline-flex';
        });
        
        // Auto-hide alerts
        setTimeout(function() {
            const alerts = document.querySelectorAll('.alert');
            alerts.forEach(alert => {
                alert.style.opacity = '0';
                setTimeout(() => alert.remove(), 500);
            });
        }, 5000);

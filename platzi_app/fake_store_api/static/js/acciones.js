// Variables globales
let formValid = false;

// Inicialización cuando carga la página
document.addEventListener('DOMContentLoaded', function() {
    initializeForm();
    if (document.getElementById('successModal')) {
        document.getElementById('successModal').style.display = 'flex';
    }
});

function initializeForm() {
    const form = document.getElementById('productForm');
    if (!form) return;
    const inputs = form.querySelectorAll('input, select, textarea');
    
    // Agregar event listeners a todos los campos
    inputs.forEach(input => {
        input.addEventListener('input', validateField);
        input.addEventListener('blur', validateField);
        input.addEventListener('change', updateProgress);
        if (input.type === 'url') {
            input.addEventListener('input', function() {
                previewImage(input.id);
            });
        }
    });
    
    // Contadores de caracteres
    setupCharacterCounters();
    
    // Validación inicial
    validateForm();
    updateProgress();
}

function setupCharacterCounters() {
    const titulo = document.getElementById('titulo');
    const descripcion = document.getElementById('descripcion');
    
    if (titulo) {
        titulo.addEventListener('input', function() {
            updateCounter('titulo-counter', this.value.length, 100);
        });
    }
    
    if (descripcion) {
        descripcion.addEventListener('input', function() {
            updateCounter('descripcion-counter', this.value.length, 500);
        });
    }
}

function updateCounter(counterId, current, max) {
    const counter = document.getElementById(counterId);
    if (!counter) return;
    counter.textContent = current;
    
    if (current > max * 0.9) {
        counter.style.color = '#ef4444';
    } else if (current > max * 0.8) {
        counter.style.color = '#f59e0b';
    } else {
        counter.style.color = '#10b981';
    }
}

function validateField(event) {
    const field = event.target;
    const fieldName = field.id;
    const value = field.value.trim();
    const errorElement = document.getElementById(fieldName + '-error');
    
    let isValid = true;
    let errorMessage = '';
    
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
            } else if (value && !isValidImageUrl(value)) {
                errorMessage = 'URL de imagen inválida. Formatos permitidos: jpg, png, gif, etc.';
                isValid = false;
            }
            break;
            
        case 'imagen2':
        case 'imagen3':
            if (value && !isValidImageUrl(value)) {
                errorMessage = 'URL de imagen inválida. Formatos permitidos: jpg, png, gif, etc.';
                isValid = false;
            }
            break;
    }
    
    if (errorElement) {
        errorElement.textContent = errorMessage;
        errorElement.style.display = errorMessage ? 'block' : 'none';
    }
    
    if (isValid) {
        field.classList.remove('error');
    } else {
        field.classList.add('error');
    }
    
    validateForm();
    updateProgress();
}

function isValidImageUrl(url) {
    const imageExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg'];
    return imageExtensions.some(ext => url.toLowerCase().endswith(ext));
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
    if (submitBtn) {
        submitBtn.disabled = !allValid;
    }
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
    
    if (progressFill) progressFill.style.width = percentage + '%';
    if (progressText) progressText.textContent = percentage + '% Completado';
}

function previewImage(fieldName) {
    const input = document.getElementById(fieldName);
    const preview = document.getElementById('preview-' + fieldName);
    const url = input.value.trim();
    
    if (preview) {
        if (url && isValidImageUrl(url)) {
            preview.innerHTML = `
                <img src="${url}" alt="Vista previa" 
                    onload="this.style.display='block'" 
                    onerror="this.parentElement.innerHTML='<p>Error al cargar la imagen</p>'"
                    style="display:none; max-width: 200px; margin-top: 10px;">
            `;
            preview.style.display = 'block';
        } else {
            preview.innerHTML = '';
            preview.style.display = 'none';
        }
    }
}

function closeModal() {
    const modal = document.getElementById('successModal');
    if (modal) modal.style.display = 'none';
}

// Envío del formulario con loading
const productForm = document.getElementById('productForm');
if (productForm) {
    productForm.addEventListener('submit', function(e) {
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
}

// Auto-hide alerts after 5 seconds
setTimeout(function() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        alert.style.opacity = '0';
        setTimeout(() => alert.remove(), 500);
    });
}, 5000); 
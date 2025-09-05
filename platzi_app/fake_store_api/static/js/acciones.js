// acciones.js - Versión mejorada con CRUD completo

// Helper function to get CSRF token from cookie
function getCSRFToken() {
    const name = 'csrftoken';
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Funcionalidades de filtrado y búsqueda
function filterProducts() {
    const category = document.getElementById('categoryFilter').value.toLowerCase();
    const cards = document.querySelectorAll('.product-card');
    
    cards.forEach(card => {
        const cardCategory = card.dataset.category.toLowerCase();
        if (!category || cardCategory.includes(category)) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
}

function searchProducts() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const cards = document.querySelectorAll('.product-card');
    
    cards.forEach(card => {
        const title = card.dataset.title;
        if (title.includes(searchTerm)) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
}

function sortProducts() {
    const sortBy = document.getElementById('sortFilter').value;
    const container = document.getElementById('productsGrid');
    const cards = Array.from(container.querySelectorAll('.product-card'));
    
    cards.sort((a, b) => {
        switch(sortBy) {
            case 'title':
                return a.dataset.title.localeCompare(b.dataset.title);
            case 'price-low':
                return parseFloat(a.dataset.price) - parseFloat(b.dataset.price);
            case 'price-high':
                return parseFloat(b.dataset.price) - parseFloat(a.dataset.price);
            default:
                return 0;
        }
    });
    
    cards.forEach(card => container.appendChild(card));
}

function openImageModal(imageSrc, title) {
    const modal = document.getElementById('imageModal');
    const modalImg = document.getElementById('modalImage');
    const caption = document.getElementById('imageCaption');
    
    modal.style.display = 'flex';
    modalImg.src = imageSrc;
    caption.textContent = title;
    document.body.style.overflow = 'hidden';
}

function closeImageModal() {
    document.getElementById('imageModal').style.display = 'none';
    document.body.style.overflow = 'auto';
}

function refreshProducts() {
    location.reload();
}

// FUNCIONES PRINCIPALES DE CRUD

function viewProduct(id) {
    console.log('Ver producto:', id);
    
    // Obtener datos del producto desde la tarjeta
    const productCard = document.querySelector(`[data-id="${id}"]`);
    if (!productCard) {
        showNotification('Producto no encontrado', 'error');
        return;
    }
    
    const title = productCard.dataset.title;
    const price = productCard.dataset.price;
    const category = productCard.dataset.category;
    const description = productCard.querySelector('.product-description')?.textContent || '';
    const imageSrc = productCard.querySelector('.card-image')?.src || '';
    
    // Crear modal personalizado para mostrar detalles
    showProductModal({
        id,
        title,
        price,
        category,
        description,
        image: imageSrc
        
    });
    
}

function editProduct(id) {
    console.log('Editando producto:', id);
    
    // Obtener datos del producto desde la tarjeta
    const productCard = document.querySelector(`[data-id="${id}"]`);
    if (!productCard) {
        showNotification('Producto no encontrado', 'error');
        return;
    }
    
    // Crear un formulario con los datos prellenados y redirigir
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = '/editar_producto/';
    form.style.display = 'none';
    
    // Agregar CSRF token
    const csrfInput = document.createElement('input');
    csrfInput.type = 'hidden';
    csrfInput.name = 'csrfmiddlewaretoken';
    csrfInput.value = getCSRFToken();
    form.appendChild(csrfInput);
    
    // Agregar ID del producto
    const idInput = document.createElement('input');
    idInput.type = 'hidden';
    idInput.name = 'product_id';
    idInput.value = id;
    form.appendChild(idInput);
    
    // Agregar datos del producto
    const titleInput = document.createElement('input');
    titleInput.type = 'hidden';
    titleInput.name = 'product_title';
    titleInput.value = productCard.dataset.title || '';
    form.appendChild(titleInput);
    
    const priceInput = document.createElement('input');
    priceInput.type = 'hidden';
    priceInput.name = 'product_price';
    priceInput.value = productCard.dataset.price || '';
    form.appendChild(priceInput);
    
    const categoryInput = document.createElement('input');
    categoryInput.type = 'hidden';
    categoryInput.name = 'product_category';
    categoryInput.value = productCard.dataset.categoryId || '';
    form.appendChild(categoryInput);
    
    const descriptionInput = document.createElement('input');
    descriptionInput.type = 'hidden';
    descriptionInput.name = 'product_description';
    descriptionInput.value = productCard.querySelector('.product-description')?.textContent || '';
    form.appendChild(descriptionInput);
    
    const imageInput = document.createElement('input');
    imageInput.type = 'hidden';
    imageInput.name = 'product_image';
    imageInput.value = productCard.querySelector('.card-image')?.src || '';
    form.appendChild(imageInput);
    
    document.body.appendChild(form);
    form.submit();
}

function deleteProduct(id) {
    if (!confirm('¿Estás seguro de que deseas eliminar este producto?')) {
        return;
    }
    
    // Mostrar indicador de carga
    const productCard = document.querySelector(`[data-id="${id}"]`);
    if (productCard) {
        productCard.style.opacity = '0.5';
        productCard.style.pointerEvents = 'none';
    }
    
    // Crear FormData para enviar el ID correctamente
    const formData = new FormData();
    formData.append('id', id);
    formData.append('csrfmiddlewaretoken', getCSRFToken());
    
    fetch('/eliminar_producto/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCSRFToken()
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            showNotification(data.message || 'Producto eliminado exitosamente', 'success');
            
            // Remover la tarjeta del producto con animación
            if (productCard) {
                productCard.style.transition = 'all 0.3s ease';
                productCard.style.transform = 'scale(0)';
                productCard.style.opacity = '0';
                
                setTimeout(() => {
                    productCard.remove();
                    updateProductCount();
                }, 300);
            }
        } else {
            throw new Error(data.error || 'Error al eliminar el producto');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification(error.message || 'Error de red al eliminar el producto', 'error');
        
        // Restaurar el estado de la tarjeta
        if (productCard) {
            productCard.style.opacity = '1';
            productCard.style.pointerEvents = 'auto';
        }
    });
}

// Función auxiliar para mostrar modal de detalles del producto
function showProductModal(product) {
    // Crear modal si no existe
    let modal = document.getElementById('productModal');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'productModal';
        modal.className = 'image-modal';
        modal.innerHTML = `
            <div class="modal-content-product">
                <button class="modal-close" onclick="closeProductModal()">&times;</button>
                <div class="modal-product-content">
                    <div class="modal-product-image">
                        <img id="modalProductImage" src="" alt="">
                    </div>
                    <div class="modal-product-details">
                        <h2 id="modalProductTitle"></h2>
                        <p class="modal-product-category" id="modalProductCategory"></p>
                        <p class="modal-product-price" id="modalProductPrice"></p>
                        <p class="modal-product-description" id="modalProductDescription"></p>
                        <p class="modal-product-id">ID: <span id="modalProductId"></span></p>
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
    }
    
    // Llenar datos del modal
    document.getElementById('modalProductImage').src = product.image;
    document.getElementById('modalProductTitle').textContent = product.title;
    document.getElementById('modalProductCategory').textContent = product.category;
    document.getElementById('modalProductPrice').textContent = `${product.price}`;
    document.getElementById('modalProductDescription').textContent = product.description;
    document.getElementById('modalProductId').textContent = product.id;
    
    // Mostrar modal
    modal.style.display = 'flex';
    document.body.style.overflow = 'hidden';
}

function closeProductModal() {
    const modal = document.getElementById('productModal');
    if (modal) {
        modal.style.display = 'none';
        document.body.style.overflow = 'auto';
    }
}

// Función para actualizar el contador de productos
function updateProductCount() {
    const remainingCards = document.querySelectorAll('.product-card').length;
    const totalElement = document.querySelector('.summary-content h3');
    if (totalElement) {
        totalElement.textContent = `${remainingCards} productos encontrados`;
    }
}

function showNotification(message, type = 'info', duration = 5000) {
    // Remover notificaciones existentes
    const existingNotifications = document.querySelectorAll('.notification');
    existingNotifications.forEach(notification => notification.remove());
    
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        ${message}
        <button class="close-notification" onclick="this.parentElement.remove()">&times;</button>
    `;
    
    // Agregar estilos CSS dinámicamente si no existen
    if (!document.getElementById('notification-styles')) {
        const styles = document.createElement('style');
        styles.id = 'notification-styles';
        styles.textContent = `
            .notification {
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 1rem 1.5rem;
                border-radius: 8px;
                color: white;
                font-weight: 600;
                z-index: 9999;
                display: flex;
                align-items: center;
                justify-content: space-between;
                min-width: 300px;
                animation: slideInRight 0.3s ease-out;
            }
            .notification-success { background-color: #10b981; }
            .notification-error { background-color: #ef4444; }
            .notification-info { background-color: #3b82f6; }
            .close-notification {
                background: none;
                border: none;
                color: white;
                font-size: 1.2rem;
                cursor: pointer;
                margin-left: 1rem;
                padding: 0;
            }
            @keyframes slideInRight {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
        `;
        document.head.appendChild(styles);
    }
    
    document.body.appendChild(notification);
    
    // Auto-remover después del tiempo especificado
    setTimeout(() => {
        if (notification.parentElement) {
            notification.style.transform = 'translateX(100%)';
            notification.style.opacity = '0';
            setTimeout(() => notification.remove(), 300);
        }
    }, duration);
}

// Inicialización cuando carga la página
document.addEventListener('DOMContentLoaded', function() {
    // Para obtener_productos
    const cards = document.querySelectorAll('.product-card');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
    });

    // Añadir eventos a los botones de acción con verificación de ID
    document.querySelectorAll('.action-btn').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const id = this.dataset.id;
            const action = this.dataset.action;
            
            if (!id) {
                showNotification('Error: ID del producto no encontrado', 'error');
                return;
            }
            
            console.log(`Ejecutando acción: ${action} para producto: ${id}`);
            
            switch(action) {
                case 'view':
                    viewProduct(id);
                    break;
                case 'edit':
                    editProduct(id);
                    break;
                case 'delete':
                    deleteProduct(id);
                    break;
                default:
                    showNotification('Acción no reconocida', 'error');
            }
        });
    });

    // Cerrar modal con ESC
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeImageModal();
            closeProductModal();
        }
    });

    // Para formularios de agregar/editar producto
    const form = document.querySelector('form');
    if (form) {
        // Contadores
        const titleInput = document.getElementById('titulo');
        const titleCounter = document.getElementById('titleCounter');
        const descInput = document.getElementById('descripcion');
        const descCounter = document.getElementById('descCounter');

        if (titleInput && titleCounter) {
            titleInput.addEventListener('input', () => {
                const len = titleInput.value.length;
                titleCounter.textContent = `${len}/100 caracteres`;
                titleCounter.className = len > 90 ? 'counter error' : len > 70 ? 'counter warning' : 'counter';
            });
        }

        if (descInput && descCounter) {
            descInput.addEventListener('input', () => {
                const len = descInput.value.length;
                descCounter.textContent = `${len}/500 caracteres`;
                descCounter.className = len > 450 ? 'counter error' : len > 350 ? 'counter warning' : 'counter';
            });
        }

        // Progress bar
        const progressBar = document.querySelector('.progress-bar');
        const progressText = document.querySelector('.progress-text');
        const inputs = form.querySelectorAll('input, select, textarea');
        
        function updateProgress() {
            const filled = Array.from(inputs).filter(input => input.value.trim() !== '').length;
            const percent = Math.round((filled / inputs.length) * 100);
            if (progressBar) progressBar.style.width = `${percent}%`;
            if (progressText) progressText.textContent = `${percent}% Completado`;
        }
        
        inputs.forEach(input => input.addEventListener('input', updateProgress));

        // Image previews
        const previewBtns = document.querySelectorAll('.preview-btn');
        previewBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const inputId = btn.previousElementSibling.id;
                const url = document.getElementById(inputId).value;
                if (url) {
                    openImageModal(url, 'Vista Previa de Imagen');
                } else {
                    showNotification('Ingresa una URL válida primero', 'error');
                }
            });
        });

        // Loading on submit
        const submitBtn = form.querySelector('button[type="submit"]');
        const loadingSpan = submitBtn?.querySelector('.btn-loading');
        if (submitBtn && loadingSpan) {
            form.addEventListener('submit', () => {
                submitBtn.disabled = true;
                loadingSpan.style.display = 'inline-block';
            });
        }
    }

    // Auto-cerrar notificaciones al hacer click
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('close-notification')) {
            e.target.parentElement.remove();
        }
    });
});
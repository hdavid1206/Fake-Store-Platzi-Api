// ... Código existente ...

// Para carrito
document.addEventListener('DOMContentLoaded', () => {
    const quantityForms = document.querySelectorAll('form[action*="update_cart_quantity"]');
    quantityForms.forEach(form => {
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            const formData = new FormData(form);
            fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: { 'X-CSRFToken': getCSRFToken() }
            }).then(() => location.reload());
        });
    });
});
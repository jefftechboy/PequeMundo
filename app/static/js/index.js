    // Función para actualizar el contador del carrito
    function actualizarContadorCarrito() {
        const carrito = JSON.parse(localStorage.getItem("carrito")) || [];
        const totalItems = carrito.length;
        const badge = document.getElementById("cartCounter");
        if (badge) badge.innerText = totalItems;
    }

    // Actualizar contador al cargar la página
    actualizarContadorCarrito();

    // Escuchar cambios en localStorage (para cuando se agregan productos desde otra pestaña)
    window.addEventListener('storage', function(e) {
        if (e.key === 'carrito') {
        actualizarContadorCarrito();
        }
    });

    console.log("🌟 PequeMundo · Espacios felices para niños");
    
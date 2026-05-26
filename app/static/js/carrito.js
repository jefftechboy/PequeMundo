  // ---------- MODELO DE DATOS ----------
  const PRODUCTOS_STORAGE_KEY = 'pequemundo_productos';
  const catalogoBase = [
    { id: 1, nombre: "Cama Montessori", precio: 129900, img: "https://cdnx.jumpseller.com/kidscool1/image/74894398/resize/540/540?1774003487" },
    { id: 2, nombre: "Escritorio Kids", precio: 84900, img: "https://www.ikea.com/cl/es/images/products/flisat-escritorio-infantil-altura-regulable-verde__1447837_pe989277_s5.jpg?f=xl" },
    { id: 3, nombre: "Repisa nube 3 en 1", precio: 49900, img: "https://form.cl/cdn/shop/files/v-muk0310849102-1-cfb9ebd3-9e97-4188-bc3e-78f9a24dc837.jpg?v=1773172866&width=1200" },
    { id: 4, nombre: "Silla Balancín", precio: 65900, img: "https://www.ikea.com/cl/es/images/products/poaeng-sillon-infantil-chapa-abedul-skogbo-motivo-animal__1409153_pe972155_s5.jpg?f=xl" },
    { id: 5, nombre: "Estantería Montessori", precio: 112900, img: "https://http2.mlstatic.com/D_NQ_NP_2X_613698-MLA96078795947_102025-F.webp" },
    { id: 6, nombre: "Mesa de actividades", precio: 78900, img: "https://media.falabella.com/falabellaCL/137398464_01/w=1200,h=1200,fit=pad" },
    { id: 7, nombre: "Cojín lectura lunar", precio: 32900, img: "https://www.bigpigkids.cl/cdn/shop/files/l1n0-moon-cushion-sand-nobodinoz-1-8435574934277_1_png.webp?v=1733867410&width=990" },
    { id: 8, nombre: "Armario infantil", precio: 189900, img: "https://media.falabella.com/sodimacCL/661907X_400/w=1200,h=1200,fit=pad" }
  ];

  function construirCatalogo() {
    const base = Object.fromEntries(catalogoBase.map(producto => [producto.id, { ...producto }]));
    const stored = localStorage.getItem(PRODUCTOS_STORAGE_KEY);
    if (!stored) return base;

    try {
      const parsed = JSON.parse(stored);
      if (!Array.isArray(parsed)) return base;

      parsed.forEach(producto => {
        if (!producto || !producto.id) return;
        base[producto.id] = {
          id: producto.id,
          nombre: producto.nombre,
          precio: producto.precio,
          img: producto.imagen || producto.img || (base[producto.id] && base[producto.id].img) || 'https://picsum.photos/200/150?blur=1'
        };
      });
    } catch (error) {
      return base;
    }

    return base;
  }

  const productosCatalogo = construirCatalogo();

  function normalizarItemCarrito(item) {
    const productoCatalogo = productosCatalogo[item.id] || {};
    const productoActual = item.producto || {};
    return {
      ...item,
      producto: {
        id: productoActual.id || productoCatalogo.id || item.id,
        nombre: productoActual.nombre || productoCatalogo.nombre || 'Producto',
        precio: productoActual.precio || productoCatalogo.precio || 0,
        img: productoActual.img || productoActual.imagen || productoCatalogo.img || 'https://picsum.photos/200/150?blur=1'
      }
    };
  }

  // Cargar carrito desde localStorage o inicial vacío
  let carrito = [];

  function cargarCarritoStorage() {
    const stored = localStorage.getItem("pequemundo_carrito");
    if (stored) {
      try {
        carrito = JSON.parse(stored).map(normalizarItemCarrito);
      } catch(e) { carrito = []; }
    } else {
      // Datos de ejemplo para mostrar carrito con contenido inicial (demo atractiva)
      // Pero para evitar vacío, dejamos demo con 2 items si está vacío por primera vez.
      if(carrito.length === 0) {
        carrito = [
          { id: 1, cantidad: 1, producto: productosCatalogo[1] },
          { id: 3, cantidad: 2, producto: productosCatalogo[3] }
        ];
        guardarCarritoStorage();
      }
    }
  }

  function guardarCarritoStorage() {
    localStorage.setItem("pequemundo_carrito", JSON.stringify(carrito));
    actualizarContadorHeader();
  }

  function actualizarContadorHeader() {
    const totalItems = carrito.reduce((sum, item) => sum + item.cantidad, 0);
    const badge = document.getElementById("cartCounter");
    if (badge) badge.innerText = totalItems;
  }

  // Funciones del carrito
  function obtenerItemIndex(id) {
    return carrito.findIndex(item => item.id === id);
  }

  function agregarAlCarrito(id, cantidad = 1) {
    const idx = obtenerItemIndex(id);
    if (idx !== -1) {
      carrito[idx].cantidad += cantidad;
    } else {
      const producto = productosCatalogo[id];
      if (producto) carrito.push(normalizarItemCarrito({ id, cantidad, producto }));
    }
    guardarCarritoStorage();
    mostrarCarrito();
  }

  function eliminarItem(id) {
    carrito = carrito.filter(item => item.id !== id);
    guardarCarritoStorage();
    mostrarCarrito();
  }

  function actualizarCantidad(id, nuevaCantidad) {
    if (nuevaCantidad <= 0) {
      eliminarItem(id);
      return;
    }
    const idx = obtenerItemIndex(id);
    if (idx !== -1) {
      carrito[idx].cantidad = nuevaCantidad;
      guardarCarritoStorage();
      mostrarCarrito();
    }
  }

  function vaciarCarrito() {
    if (carrito.length === 0) return;
    if (confirm("¿Vaciar todo el carrito? Los productos se eliminarán permanentemente.")) {
      carrito = [];
      guardarCarritoStorage();
      mostrarCarrito();
    }
  }

  function calcularTotales() {
    let subtotal = 0;
    carrito.forEach(item => {
      subtotal += item.producto.precio * item.cantidad;
    });

    const deliveryType = document.getElementById('deliveryType')?.value || 'shipping';
    const region = document.getElementById('shippingRegion')?.value || 'rm';
    const FREE_SHIP_THRESHOLD = 75000;
    let envio;
    if (deliveryType === 'pickup') {
      envio = 0;
    } else if (subtotal >= FREE_SHIP_THRESHOLD) {
      envio = 0;
    } else {
      envio = region === 'rm' ? 4990 : 8990;
    }
    const total = subtotal + envio;
    return { subtotal, envio, total, freeShipping: deliveryType !== 'pickup' && subtotal >= FREE_SHIP_THRESHOLD };
  }

  function formatearPrecio(valor) {
    return new Intl.NumberFormat('es-CL', { style: 'currency', currency: 'CLP', minimumFractionDigits: 0 }).format(valor);
  }

  function mostrarCarrito() {
    const cartItemsContainer = document.getElementById("cartItemsList");
    const cartSummaryDiv = document.getElementById("cartSummary");
    const emptyDiv = document.querySelector(".empty-cart");
    
    if (!cartItemsContainer) return;

    if (carrito.length === 0) {
      cartItemsContainer.innerHTML = "";
      cartItemsContainer.style.display = "none";
      if (emptyDiv) emptyDiv.style.display = "block";
      if (cartSummaryDiv) cartSummaryDiv.style.display = "none";
      actualizarContadorHeader();
      return;
    }
    
    if (emptyDiv) emptyDiv.style.display = "none";
    cartItemsContainer.style.display = "block";
    cartItemsContainer.innerHTML = "";
    
    carrito.forEach(item => {
      const producto = item.producto;
      const subtotalItem = producto.precio * item.cantidad;
      const itemDiv = document.createElement("div");
      itemDiv.className = "cart-item";
      
      itemDiv.innerHTML = `
        <div class="cart-item-img">
          <img src="${producto.img}" alt="${producto.nombre}" onerror="this.src='https://picsum.photos/id/20/70/70'">
        </div>
        <div class="cart-item-info">
          <h3>${producto.nombre}</h3>
          <div class="item-price">${formatearPrecio(producto.precio)} c/u</div>
        </div>
        <div class="cart-item-quantity">
          <button class="qty-minus" data-id="${producto.id}">-</button>
          <span>${item.cantidad}</span>
          <button class="qty-plus" data-id="${producto.id}">+</button>
        </div>
        <div class="cart-item-subtotal">
          ${formatearPrecio(subtotalItem)}
        </div>
        <button class="remove-item" data-id="${producto.id}"><i class="fas fa-trash-can"></i></button>
      `;
      cartItemsContainer.appendChild(itemDiv);
    });
    
    // Eventos dinámicos
    document.querySelectorAll('.qty-minus').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const id = parseInt(btn.dataset.id);
        const item = carrito.find(i => i.id === id);
        if (item) actualizarCantidad(id, item.cantidad - 1);
      });
    });
    
    document.querySelectorAll('.qty-plus').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const id = parseInt(btn.dataset.id);
        const item = carrito.find(i => i.id === id);
        if (item) actualizarCantidad(id, item.cantidad + 1);
      });
    });
    
    document.querySelectorAll('.remove-item').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const id = parseInt(btn.dataset.id);
        eliminarItem(id);
      });
    });
    
    const { subtotal, envio, total, freeShipping } = calcularTotales();
    document.getElementById("subtotalAmount").innerText = formatearPrecio(subtotal);
    const deliveryTypeVal = document.getElementById('deliveryType')?.value || 'shipping';
    document.getElementById("shippingAmount").innerText =
      deliveryTypeVal === 'pickup' ? 'Retiro en tienda (gratis)' :
      freeShipping ? '¡Gratis! 🎉' :
      formatearPrecio(envio);
    document.getElementById("totalAmount").innerText = formatearPrecio(total);
    renderFreeShipBar(subtotal);
    if (cartSummaryDiv) cartSummaryDiv.style.display = "block";
    
    actualizarContadorHeader();
  }

  function renderFreeShipBar(subtotal) {
    const bar = document.getElementById('freeShipBar');
    if (!bar) return;
    const threshold = 75000;
    const deliveryType = document.getElementById('deliveryType')?.value || 'shipping';
    if (deliveryType === 'pickup') { bar.style.display = 'none'; return; }
    bar.style.display = '';
    const fill = document.getElementById('freeShipFill');
    const text = document.getElementById('freeShipText');
    if (subtotal >= threshold) {
      bar.classList.add('achieved');
      if (fill) fill.style.width = '100%';
      if (text) text.innerHTML = '<i class="fas fa-check-circle"></i> ¡Consiguiste envío gratis!';
    } else {
      bar.classList.remove('achieved');
      const pct = Math.min(100, Math.round((subtotal / threshold) * 100));
      if (fill) fill.style.width = pct + '%';
      const falta = formatearPrecio(threshold - subtotal);
      if (text) text.innerHTML = 'Te faltan <span>' + falta + '</span> para envío gratis';
    }
  }

  function validateEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email || '');
  }

  function updateDeliveryFields() {
    const deliveryType = document.getElementById('deliveryType')?.value || 'shipping';
    const addressField = document.getElementById('addressField');
    const regionField = document.getElementById('regionField');
    if (!addressField || !regionField) return;

    const isPickup = deliveryType === 'pickup';
    addressField.style.display = isPickup ? 'none' : 'flex';
    regionField.style.display = isPickup ? 'none' : 'flex';
    mostrarCarrito();
  }

  function prefillCheckoutFromUser() {
    if (typeof getCurrentUser !== 'function') return;
    const user = getCurrentUser();
    if (!user) return;

    const nameInput = document.getElementById('checkoutName');
    const emailInput = document.getElementById('checkoutEmail');
    if (nameInput && !nameInput.value) nameInput.value = user.name || '';
    if (emailInput && !emailInput.value) emailInput.value = user.email || '';
  }
  
  function finalizarCompra() {
    if (carrito.length === 0) {
      alert("🛒 Tu carrito está vacío. Agrega productos antes de comprar.");
      return;
    }

    const checkoutName = document.getElementById('checkoutName')?.value.trim() || '';
    const checkoutEmail = document.getElementById('checkoutEmail')?.value.trim().toLowerCase() || '';
    const deliveryType = document.getElementById('deliveryType')?.value || 'shipping';
    const shippingRegion = document.getElementById('shippingRegion')?.value || 'rm';
    const shippingAddress = document.getElementById('shippingAddress')?.value.trim() || '';

    if (!checkoutName) {
      alert('Ingresa tu nombre para continuar.');
      return;
    }

    if (!checkoutEmail || !validateEmail(checkoutEmail)) {
      alert('Ingresa un correo válido para enviar la confirmación del pedido.');
      return;
    }

    if (deliveryType === 'shipping' && !shippingAddress) {
      alert('Ingresa la dirección para enviar tu pedido.');
      return;
    }

    const { total, envio } = calcularTotales();
    const estadoInicial = 'received';
    const fechaCreacion = new Date().toISOString();
    const order = {
      id: `PQM-${Date.now()}`,
      date: fechaCreacion,
      createdAt: fechaCreacion,
      items: carrito.map(item => ({
        id: item.producto.id,
        nombre: item.producto.nombre,
        cantidad: item.cantidad,
        precio: item.producto.precio
      })),
      total,
      customerName: checkoutName,
      customerEmail: checkoutEmail,
      deliveryType,
      shippingRegion: deliveryType === 'pickup' ? '' : shippingRegion,
      shippingAddress: deliveryType === 'pickup' ? '' : shippingAddress,
      shippingCost: envio,
      status: estadoInicial,
      statusHistory: [{
        status: estadoInicial,
        date: fechaCreacion,
        note: 'Pedido creado'
      }]
    };

    if (typeof upsertOrder === 'function') {
      upsertOrder(order, { name: checkoutName, email: checkoutEmail });
    }

    localStorage.setItem("pequemundo_ultimo_pedido", JSON.stringify(order));
    if (typeof addPurchaseToCurrentUser === 'function') {
      addPurchaseToCurrentUser(order);
    }

    carrito = [];
    guardarCarritoStorage();
    mostrarCarrito();

    alert(`✨ ¡Gracias por tu compra en PequeMundo! ✨\nTotal: ${formatearPrecio(total)}\n\nAhora puedes seguir el pedido desde tu cuenta.`);
    window.location.href = `pedido.html?id=${encodeURIComponent(order.id)}`;
  }
  
  // Inicializar y cargar listeners
  window.onload = () => {
    cargarCarritoStorage();
    prefillCheckoutFromUser();
    updateDeliveryFields();
    mostrarCarrito();
    
    const vaciarBtn = document.getElementById("vaciarCarritoBtn");
    if (vaciarBtn) vaciarBtn.addEventListener("click", vaciarCarrito);
    
    const finalizarBtn = document.getElementById("finalizarCompraBtn");
    if (finalizarBtn) finalizarBtn.addEventListener("click", finalizarCompra);

    const deliveryTypeSelect = document.getElementById('deliveryType');
    if (deliveryTypeSelect) deliveryTypeSelect.addEventListener('change', updateDeliveryFields);

    const regionSelect = document.getElementById('shippingRegion');
    if (regionSelect) regionSelect.addEventListener('change', mostrarCarrito);
    
    // Sincronizar el contador global del header
    actualizarContadorHeader();
  };
  
  // Exponer funciones globales para posible uso en productos (si se necesita desde otros HTML)
  window.agregarAlCarrito = agregarAlCarrito;
  window.mostrarCarritoGlobal = mostrarCarrito;

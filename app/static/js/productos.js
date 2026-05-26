  // ---------- CATÁLOGO DE PRODUCTOS ---------- 
  /* 
   
  const PRODUCTOS_STORAGE_KEY = 'pequemundo_productos';
  const defaultProductos = [
    { 
      id: 1, 
      nombre: "Cama Montessori", 
      precio: 129900, 
      categoria: "dormitorio",
      descripcion: "Cama baja estilo Montessori, bordes redondeados, madera de pino certificada.",
      imagen: "https://cdnx.jumpseller.com/kidscool1/image/74894398/resize/540/540?1774003487",
      destacado: "hot",
      oferta: false
    },
    { 
      id: 2, 
      nombre: "Escritorio Kids", 
      precio: 84900, 
      categoria: "estudio",
      descripcion: "Escritorio regulable en altura, con espacio para tablets y organizador.",
      imagen: "https://www.ikea.com/cl/es/images/products/flisat-escritorio-infantil-altura-regulable-verde__1447837_pe989277_s5.jpg?f=xl",
      destacado: "new",
      oferta: false
    },
    { 
      id: 3, 
      nombre: "Repisa nube 3 en 1", 
      precio: 49900, 
      categoria: "deco",
      descripcion: "Set de 3 repisas flotantes con diseño de nube, ideal para cuentos y juguetes.",
      imagen: "https://form.cl/cdn/shop/files/v-muk0310849102-1-cfb9ebd3-9e97-4188-bc3e-78f9a24dc837.jpg?v=1773172866&width=1200",
      destacado: null,
      oferta: true,
      precioAnterior: 69900
    },
    { 
      id: 4, 
      nombre: "Silla Balancín", 
      precio: 65900, 
      categoria: "deco",
      descripcion: "Silla mecedora ergonómica, tapizada en tela hipoalergénica.",
      imagen: "https://www.ikea.com/cl/es/images/products/poaeng-sillon-infantil-chapa-abedul-skogbo-motivo-animal__1409153_pe972155_s5.jpg?f=xl",
      destacado: null,
      oferta: false
    },
    { 
      id: 5, 
      nombre: "Estantería Montessori", 
      precio: 112900, 
      categoria: "dormitorio",
      descripcion: "Estantería baja con 3 niveles, fomenta la autonomía y el orden.",
      imagen: "https://http2.mlstatic.com/D_NQ_NP_2X_613698-MLA96078795947_102025-F.webp",
      destacado: "hot",
      oferta: false
    },
    { 
      id: 6, 
      nombre: "Mesa de actividades", 
      precio: 78900, 
      categoria: "estudio",
      descripcion: "Mesa multifunción con pizarra magnética y compartimentos.",
      imagen: "https://media.falabella.com/falabellaCL/137398464_01/w=1200,h=1200,fit=pad",
      destacado: "new",
      oferta: true,
      precioAnterior: 99900
    },
    { 
      id: 7, 
      nombre: "Cojín lectura lunar", 
      precio: 32900, 
      categoria: "deco",
      descripcion: "Cojín gigante forma de luna, perfecto para el rincón de lectura.",
      imagen: "https://www.bigpigkids.cl/cdn/shop/files/l1n0-moon-cushion-sand-nobodinoz-1-8435574934277_1_png.webp?v=1733867410&width=990",
      destacado: null,
      oferta: false
    },
    { 
      id: 8, 
      nombre: "Armario infantil", 
      precio: 189900, 
      categoria: "dormitorio",
      descripcion: "Armario de 2 cuerpos con barras regulables y diseño alegre.",
      imagen: "https://media.falabella.com/sodimacCL/661907X_400/w=1200,h=1200,fit=pad",
      destacado: null,
      oferta: false
    }
  ];

  let productos = [];

  function normalizarProducto(producto, fallback = {}) {
    return {
      ...fallback,
      ...producto,
      imagen: producto.imagen || producto.img || fallback.imagen || 'https://picsum.photos/400/400?grayscale'
    };
  }

  function cargarProductosStorage() {
    const stored = localStorage.getItem(PRODUCTOS_STORAGE_KEY);
    if (stored) {
      try {
        const parsed = JSON.parse(stored);
        if (Array.isArray(parsed) && parsed.length) {
          productos = parsed.map(producto => {
            const fallback = defaultProductos.find(item => item.id === producto.id) || {};
            return normalizarProducto(producto, fallback);
          });
          guardarProductosStorage();
          return;
        }
      } catch (e) {
        productos = [];
      }
    }
    productos = defaultProductos.map(producto => normalizarProducto(producto));
    guardarProductosStorage();
  }

  function guardarProductosStorage() {
    localStorage.setItem(PRODUCTOS_STORAGE_KEY, JSON.stringify(productos));
  }

  function getProductoById(id) {
    return productos.find(producto => producto.id === id);
  }

  function getNextProductId() {
    const ids = productos.map(producto => producto.id);
    return ids.length ? Math.max(...ids) + 1 : 1;
  }

  function isAdmin() {
    return typeof getCurrentUser === 'function' && getCurrentUser() && getCurrentUser().role === 'admin';
  }

  // ---------- CARRITO ----------
  let carrito = [];

  function cargarCarritoStorage() {
    const stored = localStorage.getItem("pequemundo_carrito");
    if (stored) {
      try {
        carrito = JSON.parse(stored);
      } catch(e) { carrito = []; }
    } else {
      carrito = [];
    }
    actualizarContadorHeader();
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

  function agregarAlCarrito(id, cantidad = 1) {
    const producto = productos.find(p => p.id === id);
    if (!producto) return;
    
    const existingItem = carrito.find(item => item.id === id);
    if (existingItem) {
      existingItem.cantidad += cantidad;
    } else {
      carrito.push({ 
        id: producto.id, 
        cantidad: cantidad, 
        producto: {
          id: producto.id,
          nombre: producto.nombre,
          precio: producto.precio,
          img: producto.imagen
        }
      });
    }
    guardarCarritoStorage();
    mostrarToast(`${producto.nombre} agregado al carrito`);
  }

  function mostrarToast(mensaje) {
    const toast = document.getElementById("toast");
    const span = toast.querySelector("span");
    span.textContent = mensaje;
    toast.classList.add("show");
    setTimeout(() => {
      toast.classList.remove("show");
    }, 2000);
  }

  function editarProducto(id) {
    if (!isAdmin()) return;
    const producto = getProductoById(id);
    if (!producto) return;

    const nombre = prompt('Editar nombre', producto.nombre);
    if (nombre === null) return;
    const descripcion = prompt('Editar descripción', producto.descripcion);
    if (descripcion === null) return;
    const precioTexto = prompt('Editar precio (sin puntos ni comas)', producto.precio.toString());
    if (precioTexto === null) return;
    const precio = parseInt(precioTexto.replace(/\D/g, ''), 10);
    const categoria = prompt('Editar categoría (dormitorio / estudio / deco)', producto.categoria);
    if (categoria === null) return;
    const imagen = prompt('Editar URL de imagen', producto.imagen);
    if (imagen === null) return;

    producto.nombre = nombre.trim() || producto.nombre;
    producto.descripcion = descripcion.trim() || producto.descripcion;
    producto.precio = Number.isFinite(precio) && precio > 0 ? precio : producto.precio;
    producto.categoria = categoria.trim() || producto.categoria;
    producto.imagen = imagen.trim() || producto.imagen;

    guardarProductosStorage();
    renderizarProductos();
    mostrarToast('Producto actualizado correctamente');
  }

  function eliminarProducto(id) {
    if (!isAdmin()) return;
    const producto = getProductoById(id);
    if (!producto) return;

    if (!confirm(`¿Eliminar ${producto.nombre}? Esta acción no se puede deshacer.`)) {
      return;
    }

    productos = productos.filter(item => item.id !== id);
    guardarProductosStorage();
    renderizarProductos();
    mostrarToast('Producto eliminado');
  }

  function agregarProductoAdmin() {
    if (!isAdmin()) return;

    const nombre = prompt('Nombre del nuevo producto');
    if (!nombre) return;
    const descripcion = prompt('Descripción del producto');
    if (descripcion === null) return;
    const precioTexto = prompt('Precio del producto (sin puntos ni comas)');
    if (!precioTexto) return;
    const precio = parseInt(precioTexto.replace(/\D/g, ''), 10);
    const categoria = prompt('Categoría (dormitorio / estudio / deco)', 'deco');
    if (!categoria) return;
    const imagen = prompt('URL de la imagen', 'https://picsum.photos/400/400');
    if (!imagen) return;

    const nuevoProducto = {
      id: getNextProductId(),
      nombre: nombre.trim(),
      precio: Number.isFinite(precio) && precio > 0 ? precio : 0,
      categoria: categoria.trim() || 'deco',
      descripcion: descripcion.trim(),
      imagen: imagen.trim(),
      destacado: null,
      oferta: false
    };

    productos.push(nuevoProducto);
    guardarProductosStorage();
    renderizarProductos();
    mostrarToast('Producto agregado al catálogo');
  }

  // ---------- RENDER PRODUCTOS CON FILTROS ----------
  let filtroActual = "all";
  let busquedaActual = "";

  function buscarProductos(valor) {
    busquedaActual = valor.trim().toLowerCase();
    renderizarProductos();
  }

  function renderizarProductos() {
    const grid = document.getElementById("productosGrid");
    if (!grid) return;
    
    let productosFiltrados = productos;
    if (filtroActual !== "all") {
      productosFiltrados = productos.filter(p => p.categoria === filtroActual);
    }

    if (busquedaActual) {
      productosFiltrados = productosFiltrados.filter(p =>
        p.nombre.toLowerCase().includes(busquedaActual) ||
        p.descripcion.toLowerCase().includes(busquedaActual) ||
        p.categoria.toLowerCase().includes(busquedaActual)
      );
    }
    
    if (productosFiltrados.length === 0) {
      const mensaje = busquedaActual ?
        `No encontramos productos para "${busquedaActual}"` :
        `No encontramos productos en esta categoría`;
      grid.innerHTML = `<div style="text-align: center; grid-column: 1/-1; padding: 3rem;">
        <i class="fas fa-search" style="font-size: 3rem; color: #f0cfaa;"></i>
        <p style="margin-top: 1rem;">${mensaje}</p>
      </div>`;
      return;
    }
    
    grid.innerHTML = productosFiltrados.map(producto => {
      let badgeHtml = '';
      if (producto.destacado === 'hot') {
        badgeHtml = '<div class="card-badge hot"><i class="fas fa-fire"></i> Destacado</div>';
      } else if (producto.destacado === 'new') {
        badgeHtml = '<div class="card-badge new"><i class="fas fa-sparkle"></i> Nuevo</div>';
      } else if (producto.oferta) {
        badgeHtml = '<div class="card-badge"><i class="fas fa-tag"></i> Oferta</div>';
      }
      
      const precioDisplay = producto.oferta && producto.precioAnterior ? 
        `<div class="price">$${producto.precio.toLocaleString('es-CL')} <span class="original-price">$${producto.precioAnterior.toLocaleString('es-CL')}</span></div>` :
        `<div class="price">$${producto.precio.toLocaleString('es-CL')}</div>`;
      
      return `
        <div class="card" data-id="${producto.id}">
          ${badgeHtml}
          <img src="${producto.imagen}" alt="${producto.nombre}" loading="lazy">
          <h3>${producto.nombre}</h3>
          <div class="card-description">${producto.descripcion}</div>
          ${precioDisplay}
          <div class="card-actions">
            <button class="btn-buy" data-id="${producto.id}">
              <i class="fas fa-cart-plus"></i> Comprar
            </button>
            <button class="btn-detail" data-id="${producto.id}">
              <i class="fas fa-eye"></i>
            </button>
            ${isAdmin() ? `
              <button class="btn-admin-edit" data-id="${producto.id}">
                <i class="fas fa-edit"></i> Editar
              </button>
              <button class="btn-admin-delete" data-id="${producto.id}">
                <i class="fas fa-trash-alt"></i> Eliminar
              </button>
            ` : ''}
          </div>
        </div>
      `;
    }).join('');
    
    // Agregar event listeners a los botones
    document.querySelectorAll('.btn-buy').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const id = parseInt(btn.dataset.id);
        agregarAlCarrito(id);
      });
    });
    
    document.querySelectorAll('.btn-detail').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const id = parseInt(btn.dataset.id);
        const producto = productos.find(p => p.id === id);
        if (producto) {
          alert(`📦 ${producto.nombre}\n💰 Precio: $${producto.precio.toLocaleString('es-CL')}\n📝 ${producto.descripcion}\n\nAgrégalo al carrito para continuar.`);
        }
      });
    });

    document.querySelectorAll('.btn-admin-edit').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        editarProducto(parseInt(btn.dataset.id));
      });
    });

    document.querySelectorAll('.btn-admin-delete').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        eliminarProducto(parseInt(btn.dataset.id));
      });
    });
    
    // Click en la tarjeta también puede mostrar detalle (opcional)
    document.querySelectorAll('.card').forEach(card => {
      card.addEventListener('click', (e) => {
        if (e.target.closest('.btn-buy') || e.target.closest('.btn-detail')) return;
        const id = parseInt(card.dataset.id);
        const producto = productos.find(p => p.id === id);
        if (producto) {
          alert(`🛒 ${producto.nombre}\n💲 ${producto.precio.toLocaleString('es-CL')}\n✨ ${producto.descripcion}`);
        }
      });
    });
  }

  // Configurar filtros
  function initFilters() {
    const filterBtns = document.querySelectorAll('.filter-btn');
    filterBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        filterBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        filtroActual = btn.dataset.filter;
        renderizarProductos();
      });
    });
  }

  function initSearch() {
    const searchInput = document.getElementById('searchInput');
    const clearSearch = document.getElementById('clearSearch');
    if (!searchInput) return;

    searchInput.addEventListener('input', () => {
      buscarProductos(searchInput.value);
    });

    if (clearSearch) {
      clearSearch.addEventListener('click', () => {
        searchInput.value = '';
        buscarProductos('');
        searchInput.focus();
      });
    }
  }

  // Inicializar todo
  function renderAdminControls() {
    const adminControls = document.getElementById('adminControls');
    if (!adminControls) return;
    adminControls.classList.toggle('hidden', !isAdmin());
  }

  function init() {
    cargarProductosStorage();
    cargarCarritoStorage();
    renderAdminControls();
    renderizarProductos();
    initFilters();
    initSearch();

    const addButton = document.getElementById('btnAddProduct');
    if (addButton) {
      addButton.addEventListener('click', () => agregarProductoAdmin());
    }
  }
  
  // Ejecutar cuando el DOM esté listo
  document.addEventListener('DOMContentLoaded', init);
  
  // Exponer funciones globalmente
  window.agregarAlCarrito = agregarAlCarrito;
   */
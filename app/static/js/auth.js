const AUTH_STORAGE_KEY = 'pequemundo_user';
const USERS_STORAGE_KEY = 'pequemundo_users';
const ORDERS_STORAGE_KEY = 'pequemundo_orders';

const ORDER_STATUSES = [
  {
    id: 'received',
    label: 'Pedido recibido',
    shortLabel: 'Recibido',
    description: 'Recibimos tu compra y estamos preparando los siguientes pasos.',
    adminLabel: 'Recibido',
    icon: 'fa-receipt',
    step: 1
  },
  {
    id: 'preparing',
    label: 'En preparación',
    shortLabel: 'Preparación',
    description: 'Tu pedido está siendo preparado en nuestro taller.',
    adminLabel: 'En preparación',
    icon: 'fa-box-open',
    step: 2
  },
  {
    id: 'shipping',
    label: 'En camino',
    shortLabel: 'En camino',
    description: 'Tu pedido salió a reparto y va rumbo a tu domicilio.',
    adminLabel: 'En camino',
    icon: 'fa-truck',
    step: 3
  },
  {
    id: 'delivered',
    label: 'Entregado',
    shortLabel: 'Entregado',
    description: 'Tu pedido fue entregado. Esperamos que lo disfrutes.',
    adminLabel: 'Entregado',
    icon: 'fa-house',
    step: 4
  }
];

function getCurrentUser() {
  const raw = localStorage.getItem(AUTH_STORAGE_KEY);
  if (!raw) return null;

  try {
    return JSON.parse(raw);
  } catch (error) {
    return null;
  }
}

function saveCurrentUser(user) {
  const safeUser = {
    name: user.name,
    email: user.email,
    role: user.role || 'customer',
    rut: user.rut || '',
    purchaseHistory: Array.isArray(user.purchaseHistory) ? user.purchaseHistory : []
  };
  localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(safeUser));
}

function getStoredUsers() {
  const raw = localStorage.getItem(USERS_STORAGE_KEY);
  if (!raw) return [];

  try {
    return JSON.parse(raw);
  } catch (error) {
    return [];
  }
}

function saveStoredUsers(users) {
  localStorage.setItem(USERS_STORAGE_KEY, JSON.stringify(users));
}

function getStoredOrders() {
  const raw = localStorage.getItem(ORDERS_STORAGE_KEY);
  if (!raw) return [];

  try {
    return JSON.parse(raw).map(order => ensureOrderShape(order)).sort(sortOrdersByDateDesc);
  } catch (error) {
    return [];
  }
}

function saveStoredOrders(orders) {
  const normalizedOrders = orders.map(order => ensureOrderShape(order)).sort(sortOrdersByDateDesc);
  localStorage.setItem(ORDERS_STORAGE_KEY, JSON.stringify(normalizedOrders));
}

function ensureUserProfile(user) {
  if (!user.role) {
    user.role = 'customer';
  }

  if (!Array.isArray(user.purchaseHistory)) {
    user.purchaseHistory = [];
  }

  return user;
}

function updateStoredUser(user, options = {}) {
  const users = getStoredUsers();
  const normalizedEmail = user.email.trim().toLowerCase();
  const index = users.findIndex(u => u.email.toLowerCase() === normalizedEmail);
  const updatedUser = ensureUserProfile({ ...user, email: normalizedEmail });

  if (index === -1) {
    users.push(updatedUser);
  } else {
    users[index] = updatedUser;
  }

  saveStoredUsers(users);
  if (options.syncCurrent !== false) {
    saveCurrentUser(updatedUser);
  }

  return updatedUser;
}

function findUserByEmail(email) {
  const normalized = email.trim().toLowerCase();
  return getStoredUsers().find(user => user.email.toLowerCase() === normalized);
}

function ensureDefaultAdmin() {
  const users = getStoredUsers();
  if (!users.some(user => user.email.toLowerCase() === 'admin@pequemundo.cl')) {
    users.push({
      name: 'Administrador PequeMundo',
      email: 'admin@pequemundo.cl',
      password: 'admin123',
      role: 'admin',
      purchaseHistory: []
    });
    saveStoredUsers(users);
  }
}

function isAdminUser(user) {
  return user && user.role === 'admin';
}

function getOrderStatuses() {
  return ORDER_STATUSES.slice();
}

function getOrderStatusMeta(status) {
  return ORDER_STATUSES.find(item => item.id === status) || ORDER_STATUSES[0];
}

function sortOrdersByDateDesc(left, right) {
  return new Date(right.createdAt || right.date || 0) - new Date(left.createdAt || left.date || 0);
}

function normalizeOrderItems(items) {
  if (!Array.isArray(items)) return [];

  return items
    .map(item => ({
      id: item.id,
      nombre: item.nombre,
      cantidad: Number(item.cantidad) || 0,
      precio: Number(item.precio) || 0
    }))
    .filter(item => item.nombre && item.cantidad > 0);
}

function ensureOrderShape(order, customer = {}) {
  const createdAt = order.createdAt || order.date || new Date().toISOString();
  const meta = getOrderStatusMeta(order.status);
  const items = normalizeOrderItems(order.items);
  const deliveryType = order.deliveryType === 'pickup' ? 'pickup' : 'shipping';
  const shippingRegion = deliveryType === 'pickup' ? '' : (order.shippingRegion || 'rm');
  const shippingAddress = deliveryType === 'pickup' ? '' : String(order.shippingAddress || '').trim();
  const shippingCost = deliveryType === 'pickup' ? 0 : Math.max(0, Number(order.shippingCost) || 0);
  const total = typeof order.total === 'number'
    ? order.total
    : items.reduce((sum, item) => sum + (item.precio * item.cantidad), 0) + shippingCost;

  const normalizedHistory = Array.isArray(order.statusHistory) && order.statusHistory.length > 0
    ? order.statusHistory.map(entry => ({
        status: getOrderStatusMeta(entry.status).id,
        date: entry.date || createdAt,
        note: entry.note || ''
      }))
    : [{
        status: meta.id,
        date: createdAt,
        note: 'Pedido creado'
      }];

  return {
    id: order.id || `PQM-${Date.now()}`,
    date: createdAt,
    createdAt,
    updatedAt: order.updatedAt || normalizedHistory[normalizedHistory.length - 1].date || createdAt,
    items,
    total,
    customerEmail: (order.customerEmail || customer.email || '').trim().toLowerCase(),
    customerName: order.customerName || customer.name || 'Cliente PequeMundo',
    deliveryType,
    shippingRegion,
    shippingAddress,
    shippingCost,
    status: meta.id,
    statusLabel: meta.label,
    trackingMessage: meta.description,
    step: meta.step,
    statusHistory: normalizedHistory
  };
}

function mergeOrders(...sources) {
  const ordersById = new Map();

  sources.flat().forEach(order => {
    const normalized = ensureOrderShape(order, order);
    const existing = ordersById.get(normalized.id);
    if (!existing || new Date(normalized.updatedAt) >= new Date(existing.updatedAt)) {
      ordersById.set(normalized.id, normalized);
    }
  });

  return Array.from(ordersById.values()).sort(sortOrdersByDateDesc);
}

function getAllOrders() {
  const orders = getStoredOrders();
  const userOrders = getStoredUsers()
    .flatMap(user => ensureUserProfile(user).purchaseHistory.map(order => ensureOrderShape(order, user)));

  return mergeOrders(orders, userOrders);
}

function findOrderById(orderId) {
  if (!orderId) return null;
  return getAllOrders().find(order => order.id === orderId) || null;
}

function getOrdersForUser(email) {
  const normalizedEmail = (email || '').trim().toLowerCase();
  if (!normalizedEmail) return [];
  return getAllOrders().filter(order => order.customerEmail === normalizedEmail).sort(sortOrdersByDateDesc);
}

function syncOrderToUser(order) {
  if (!order.customerEmail) return;

  const storedUser = findUserByEmail(order.customerEmail);
  if (!storedUser) return;

  const normalizedUser = ensureUserProfile({ ...storedUser });
  const filteredHistory = normalizedUser.purchaseHistory.filter(item => item.id !== order.id);
  normalizedUser.purchaseHistory = [order, ...filteredHistory].map(item => ensureOrderShape(item, normalizedUser)).sort(sortOrdersByDateDesc);
  updateStoredUser(normalizedUser, { syncCurrent: false });

  const current = getCurrentUser();
  if (current && current.email.toLowerCase() === order.customerEmail) {
    saveCurrentUser({ ...current, purchaseHistory: normalizedUser.purchaseHistory });
  }
}

function upsertOrder(order, customer = {}) {
  const normalizedOrder = ensureOrderShape(order, customer);
  const orders = getStoredOrders();
  const index = orders.findIndex(item => item.id === normalizedOrder.id);

  if (index === -1) {
    orders.unshift(normalizedOrder);
  } else {
    orders[index] = normalizedOrder;
  }

  saveStoredOrders(orders);
  syncOrderToUser(normalizedOrder);

  const lastOrderRaw = localStorage.getItem('pequemundo_ultimo_pedido');
  if (lastOrderRaw) {
    try {
      const lastOrder = JSON.parse(lastOrderRaw);
      if (lastOrder.id === normalizedOrder.id) {
        localStorage.setItem('pequemundo_ultimo_pedido', JSON.stringify(normalizedOrder));
      }
    } catch (error) {
      localStorage.setItem('pequemundo_ultimo_pedido', JSON.stringify(normalizedOrder));
    }
  }

  return normalizedOrder;
}

function deleteOrderById(orderId) {
  if (!orderId) return false;

  const orders = getStoredOrders();
  const nextOrders = orders.filter(order => order.id !== orderId);
  const orderRemoved = nextOrders.length !== orders.length;

  if (!orderRemoved) {
    return false;
  }

  saveStoredOrders(nextOrders);

  const users = getStoredUsers().map(user => {
    const normalized = ensureUserProfile({ ...user });
    normalized.purchaseHistory = normalized.purchaseHistory
      .filter(order => order.id !== orderId)
      .map(order => ensureOrderShape(order, normalized));
    return normalized;
  });

  saveStoredUsers(users);

  const current = getCurrentUser();
  if (current) {
    const refreshed = users.find(user => user.email.toLowerCase() === current.email.toLowerCase());
    if (refreshed) {
      saveCurrentUser(refreshed);
    }
  }

  const lastOrderRaw = localStorage.getItem('pequemundo_ultimo_pedido');
  if (lastOrderRaw) {
    try {
      const lastOrder = JSON.parse(lastOrderRaw);
      if (lastOrder.id === orderId) {
        localStorage.removeItem('pequemundo_ultimo_pedido');
      }
    } catch (error) {
      localStorage.removeItem('pequemundo_ultimo_pedido');
    }
  }

  return true;
}

function updateOrderStatus(orderId, nextStatus, note = 'Estado actualizado por administración') {
  const currentOrder = findOrderById(orderId);
  if (!currentOrder) return null;

  const meta = getOrderStatusMeta(nextStatus);
  const now = new Date().toISOString();
  const nextHistory = currentOrder.statusHistory.slice();
  const lastEntry = nextHistory[nextHistory.length - 1];

  if (!lastEntry || lastEntry.status !== meta.id) {
    nextHistory.push({ status: meta.id, date: now, note });
  } else {
    lastEntry.date = now;
    lastEntry.note = note;
  }

  return upsertOrder({
    ...currentOrder,
    status: meta.id,
    updatedAt: now,
    statusHistory: nextHistory
  });
}

function removeOrdersForUser(email) {
  const normalizedEmail = email.trim().toLowerCase();
  const filteredOrders = getStoredOrders().filter(order => order.customerEmail !== normalizedEmail);
  saveStoredOrders(filteredOrders);
}

ensureDefaultAdmin();

function validateRutFormat(rut) {
  return /^\d{7,8}-[\dkK]$/.test(rut) || /^\d{1,2}\.\d{3}\.\d{3}-[\dkK]$/.test(rut);
}

function registerUser({ name, email, password, rut = '' }) {
  const normalizedEmail = email.trim().toLowerCase();
  if (findUserByEmail(normalizedEmail)) {
    return { success: false, message: 'Ya existe una cuenta con ese correo.' };
  }

  const newUser = {
    name: name.trim(),
    email: normalizedEmail,
    password: password.trim(),
    role: 'customer',
    rut: rut.trim(),
    purchaseHistory: []
  };

  const users = getStoredUsers();
  users.push(newUser);
  saveStoredUsers(users);
  saveCurrentUser(newUser);
  return { success: true };
}

function logoutUser() {
  localStorage.removeItem(AUTH_STORAGE_KEY);
  window.location.href = 'index.html';
}

function requireAuth() {
  const user = getCurrentUser();
  if (!user) {
    window.location.href = 'login.html';
    return false;
  }
  return true;
}

function redirectIfLoggedIn() {
  const user = getCurrentUser();
  if (user) {
    window.location.href = 'account.html';
  }
}

function initAuthPage() {
  const user = getCurrentUser();
  document.querySelectorAll('.user-link').forEach(link => {
    link.href = user ? 'account.html' : 'login.html';
  });
  document.querySelectorAll('.header-user-name').forEach(el => {
    el.textContent = user ? `Hola, ${user.name}` : '';
  });
}

function handleLogin(event) {
  event.preventDefault();
  const email = document.getElementById('email').value.trim();
  const password = document.getElementById('password').value.trim();

  clearAuthError();

  if (!email || !password) {
    showAuthError('Ingresa tu correo y contraseña.');
    return;
  }

  if (!validateEmail(email)) {
    showAuthError('Ingresa un correo válido.');
    return;
  }

  if (password.length < 6) {
    showAuthError('La contraseña debe tener al menos 6 caracteres.');
    return;
  }

  const storedUser = findUserByEmail(email);
  if (!storedUser) {
    showAuthError('No existe una cuenta con ese correo. Crea una cuenta primero.');
    return;
  }

  if (storedUser.password !== password) {
    showAuthError('Contraseña incorrecta.');
    return;
  }

  const loggedUser = ensureUserProfile(storedUser);
  updateStoredUser(loggedUser);
  window.location.href = 'account.html';
}

function handleRegister(event) {
  event.preventDefault();
  const name = document.getElementById('registerName').value.trim();
  const rut = (document.getElementById('registerRut')?.value || '').trim();
  const email = document.getElementById('registerEmail').value.trim();
  const password = document.getElementById('registerPassword').value.trim();
  const confirmPassword = document.getElementById('registerPasswordConfirm').value.trim();

  clearAuthError();

  if (!name || !email || !password || !confirmPassword) {
    showAuthError('Completa todos los campos para crear tu cuenta.');
    return;
  }

  if (rut && !validateRutFormat(rut)) {
    showAuthError('El RUT ingresado no tiene un formato válido. Ej: 12345678-9');
    return;
  }

  if (!validateEmail(email)) {
    showAuthError('Ingresa un correo válido.');
    return;
  }

  if (password.length < 6) {
    showAuthError('La contraseña debe tener al menos 6 caracteres.');
    return;
  }

  if (password !== confirmPassword) {
    showAuthError('Las contraseñas no coinciden.');
    return;
  }

  const result = registerUser({ name, email, password, rut });
  if (!result.success) {
    showAuthError(result.message);
    return;
  }

  window.location.href = 'account.html';
}

function showAuthError(message) {
  const error = document.getElementById('authError');
  if (error) {
    error.textContent = message;
    error.style.display = 'block';
  }
}

function clearAuthError() {
  const error = document.getElementById('authError');
  if (error) {
    error.textContent = '';
    error.style.display = 'none';
  }
}

function validateEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function formatNameFromEmail(email) {
  const raw = email.split('@')[0].replace(/[._-]/g, ' ');
  return raw
    .split(' ')
    .filter(Boolean)
    .map(word => word[0].toUpperCase() + word.slice(1))
    .join(' ') || 'Cliente';
}

function formatPrice(value) {
  return new Intl.NumberFormat('es-CL', {
    style: 'currency',
    currency: 'CLP',
    minimumFractionDigits: 0
  }).format(value || 0);
}

function formatOrderDate(dateString) {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleDateString('es-CL', { year: 'numeric', month: 'long', day: 'numeric' });
}

function formatOrderDateTime(dateString) {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleString('es-CL', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
}

function escapeHtml(value) {
  return String(value || '').replace(/[&<>"']/g, char => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;'
  }[char] || char));
}

function getDeliveryTypeLabel(order) {
  return order.deliveryType === 'pickup' ? 'Retiro en tienda' : 'Despacho a domicilio';
}

function getShippingRegionLabel(region) {
  return region === 'otra' ? 'Otras regiones' : 'Región Metropolitana';
}

function buildReceiptHtml(order) {
  const normalized = ensureOrderShape(order);
  const subtotal = Math.max(0, normalized.total - (normalized.shippingCost || 0));
  const address = normalized.deliveryType === 'pickup'
    ? 'No aplica (retiro en tienda)'
    : (normalized.shippingAddress || 'Dirección no informada');
  const region = normalized.deliveryType === 'pickup' ? 'No aplica' : getShippingRegionLabel(normalized.shippingRegion);
  const rows = normalized.items.map(item => `
    <tr>
      <td>${escapeHtml(item.nombre)}</td>
      <td>${item.cantidad}</td>
      <td>${formatPrice(item.precio)}</td>
      <td>${formatPrice(item.precio * item.cantidad)}</td>
    </tr>
  `).join('');

  return `<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Boleta ${escapeHtml(normalized.id)} · PequeMundo</title>
  <style>
    * { box-sizing: border-box; }
    body { font-family: Arial, sans-serif; color: #2d2a24; margin: 0; padding: 24px; }
    .sheet { max-width: 880px; margin: 0 auto; border: 1px solid #ead8c3; border-radius: 12px; padding: 20px; }
    .head { display: flex; justify-content: space-between; gap: 12px; border-bottom: 1px solid #f0e2d0; padding-bottom: 14px; margin-bottom: 16px; }
    .brand h1 { margin: 0 0 4px; font-size: 24px; }
    .brand p { margin: 2px 0; color: #6f6458; font-size: 13px; }
    .boleta-id { text-align: right; }
    .boleta-id strong { display: block; font-size: 16px; }
    .meta { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; margin-bottom: 16px; }
    .meta-box { background: #fff8ef; border: 1px solid #f3dfc3; border-radius: 10px; padding: 10px 12px; }
    .meta-box b { display: block; margin-bottom: 4px; }
    table { width: 100%; border-collapse: collapse; margin-bottom: 16px; }
    th, td { padding: 10px; border-bottom: 1px solid #f0e2d0; text-align: left; font-size: 14px; }
    th { background: #fff7ec; }
    .totals { margin-left: auto; width: 320px; }
    .totals div { display: flex; justify-content: space-between; padding: 6px 0; }
    .totals .grand { font-size: 17px; font-weight: 700; border-top: 1px solid #f0e2d0; margin-top: 6px; padding-top: 10px; }
    .foot { margin-top: 20px; color: #6f6458; font-size: 13px; }
    @media print {
      body { padding: 0; }
      .sheet { border: none; border-radius: 0; }
    }
  </style>
</head>
<body>
  <div class="sheet">
    <div class="head">
      <div class="brand">
        <h1>PequeMundo</h1>
        <p>Boleta de compra</p>
        <p>Contacto: hola@pequemundo.cl · +56 9 2395 3217</p>
      </div>
      <div class="boleta-id">
        <strong>${escapeHtml(normalized.id)}</strong>
        <span>${escapeHtml(formatOrderDateTime(normalized.createdAt))}</span>
      </div>
    </div>

    <div class="meta">
      <div class="meta-box">
        <b>Cliente</b>
        <div>${escapeHtml(normalized.customerName || 'Cliente PequeMundo')}</div>
        <div>${escapeHtml(normalized.customerEmail || 'Sin correo')}</div>
      </div>
      <div class="meta-box">
        <b>Entrega</b>
        <div>${escapeHtml(getDeliveryTypeLabel(normalized))}</div>
        <div>Región: ${escapeHtml(region)}</div>
        <div>Dirección: ${escapeHtml(address)}</div>
      </div>
    </div>

    <table>
      <thead>
        <tr>
          <th>Producto</th>
          <th>Cantidad</th>
          <th>Precio unitario</th>
          <th>Subtotal</th>
        </tr>
      </thead>
      <tbody>${rows}</tbody>
    </table>

    <div class="totals">
      <div><span>Subtotal</span><span>${formatPrice(subtotal)}</span></div>
      <div><span>Envío</span><span>${formatPrice(normalized.shippingCost || 0)}</span></div>
      <div class="grand"><span>Total</span><span>${formatPrice(normalized.total)}</span></div>
    </div>

    <div class="foot">
      Gracias por comprar en PequeMundo. Esta boleta se genera automáticamente con los datos del pedido.
    </div>
  </div>
</body>
</html>`;
}

function printOrderReceipt(orderId) {
  const order = findOrderById(orderId);
  if (!order) {
    alert('No encontramos el pedido para generar la boleta.');
    return;
  }

  const receiptWindow = window.open('', '_blank', 'width=980,height=760');
  if (!receiptWindow) {
    alert('No se pudo abrir la boleta. Revisa si el navegador bloqueó la ventana emergente.');
    return;
  }

  receiptWindow.document.open();
  receiptWindow.document.write(buildReceiptHtml(order));
  receiptWindow.document.close();
  receiptWindow.focus();
  receiptWindow.print();
}

function getCurrentUserPurchases() {
  const user = getCurrentUser();
  if (!user) return [];
  return getOrdersForUser(user.email);
}

function addPurchaseToCurrentUser(order) {
  const current = getCurrentUser();
  if (!current) return false;

  const normalizedOrder = upsertOrder({
    ...order,
    customerEmail: current.email,
    customerName: current.name,
    status: order.status || 'received',
    statusHistory: order.statusHistory || [{
      status: order.status || 'received',
      date: order.createdAt || order.date || new Date().toISOString(),
      note: 'Pedido creado'
    }]
  }, current);

  return Boolean(normalizedOrder);
}

function renderPurchaseHistory() {
  const container = document.getElementById('purchaseHistoryList');
  if (!container) return;

  const purchases = getCurrentUserPurchases();
  if (purchases.length === 0) {
    container.innerHTML = '<div class="empty-purchases">Aún no tienes pedidos registrados. Cuando compres, podrás seguirlos desde aquí.</div>';
    return;
  }

  const html = purchases.map(order => {
    const statusMeta = getOrderStatusMeta(order.status);
    const itemsHtml = order.items.map(item => `
      <div class="purchase-item">
        <span>${item.nombre} x${item.cantidad}</span>
        <strong>${formatPrice(item.precio * item.cantidad)}</strong>
      </div>
    `).join('');

    return `
      <div class="purchase-card">
        <div class="purchase-header">
          <div>
            <div class="purchase-id">Pedido ${order.id || 'sin número'}</div>
            <div class="purchase-date">${formatOrderDate(order.createdAt)}</div>
          </div>
          <span class="status-badge status-${statusMeta.id}">${statusMeta.shortLabel}</span>
        </div>
        <div class="purchase-message">${statusMeta.description}</div>
        <div class="purchase-items">${itemsHtml}</div>
        <div class="purchase-footer-row">
          <div class="purchase-total">Total: ${formatPrice(order.total)}</div>
          <div style="display:flex; gap:0.6rem; flex-wrap:wrap;">
            <button class="track-order-link receipt-link" type="button" data-order-id="${order.id}">Ver boleta</button>
            <a class="track-order-link" href="pedido.html?id=${encodeURIComponent(order.id)}">Ver seguimiento</a>
          </div>
        </div>
      </div>
    `;
  }).join('');

  container.innerHTML = html;

  container.querySelectorAll('.receipt-link').forEach(button => {
    button.addEventListener('click', () => {
      printOrderReceipt(button.dataset.orderId);
    });
  });
}

function renderAdminOrders() {
  const section = document.getElementById('adminOrdersSection');
  const container = document.getElementById('adminOrdersList');
  if (!section || !container) return;

  const current = getCurrentUser();
  const isAdmin = isAdminUser(current);
  section.hidden = !isAdmin;
  if (!isAdmin) return;

  const orders = getAllOrders();
  if (orders.length === 0) {
    container.innerHTML = '<div class="empty-purchases">Todavía no hay pedidos para administrar.</div>';
    return;
  }

  const optionsHtml = getOrderStatuses().map(status => `
    <option value="${status.id}">${status.adminLabel}</option>
  `).join('');

  container.innerHTML = orders.map(order => `
    <div class="admin-order-card">
      <div class="admin-order-head">
        <div>
          <strong>${order.id}</strong>
          <span>${order.customerName} · ${order.customerEmail || 'sin correo'}</span>
        </div>
        <span class="status-badge status-${order.status}">${getOrderStatusMeta(order.status).shortLabel}</span>
      </div>
      <div class="admin-order-meta">
        <span>Total ${formatPrice(order.total)}</span>
        <span>Región ${order.deliveryType === 'pickup' ? 'No aplica' : getShippingRegionLabel(order.shippingRegion)}</span>
        <span>Dirección ${order.deliveryType === 'pickup' ? 'No aplica (retiro en tienda)' : (order.shippingAddress || 'No informada')}</span>
        <span>Creado ${formatOrderDateTime(order.createdAt)}</span>
        <span>Última actualización ${formatOrderDateTime(order.updatedAt)}</span>
      </div>
      <div class="admin-order-items">${order.items.map(item => `${item.nombre} x${item.cantidad}`).join(' · ')}</div>
      <div class="admin-order-controls">
        <select class="admin-status-select" data-order-id="${order.id}">
          ${optionsHtml}
        </select>
        <button class="admin-save-btn" type="button" data-order-id="${order.id}">Actualizar estado</button>
        <button class="admin-delete-btn" type="button" data-order-id="${order.id}">Eliminar pedido</button>
        <button class="track-order-link admin-receipt-link" type="button" data-order-id="${order.id}">Ver boleta</button>
        <a class="track-order-link" href="pedido.html?id=${encodeURIComponent(order.id)}">Ver pedido</a>
      </div>
    </div>
  `).join('');

  container.querySelectorAll('.admin-status-select').forEach(select => {
    const order = findOrderById(select.dataset.orderId);
    select.value = order ? order.status : 'received';
  });

  container.querySelectorAll('.admin-save-btn').forEach(button => {
    button.addEventListener('click', () => {
      const orderId = button.dataset.orderId;
      const select = container.querySelector(`.admin-status-select[data-order-id="${orderId}"]`);
      if (!select) return;

      updateOrderStatus(orderId, select.value);
      renderAdminOrders();
      renderPurchaseHistory();
      alert('Estado del pedido actualizado correctamente.');
    });
  });

  container.querySelectorAll('.admin-delete-btn').forEach(button => {
    button.addEventListener('click', () => {
      const orderId = button.dataset.orderId;
      const confirmed = confirm(`¿Eliminar el pedido ${orderId}? Esta acción no se puede deshacer.`);
      if (!confirmed) return;

      const removed = deleteOrderById(orderId);
      if (!removed) {
        alert('No se pudo eliminar el pedido.');
        return;
      }

      renderAdminOrders();
      renderPurchaseHistory();
      alert('Pedido eliminado correctamente.');
    });
  });

  container.querySelectorAll('.admin-receipt-link').forEach(button => {
    button.addEventListener('click', () => {
      printOrderReceipt(button.dataset.orderId);
    });
  });
}

function clearPurchaseHistory() {
  const current = getCurrentUser();
  if (!current) return;
  if (!confirm('¿Estás seguro de vaciar tu historial de compras? Esta acción no se puede deshacer.')) return;

  const storedUser = findUserByEmail(current.email);
  if (!storedUser) return;

  storedUser.purchaseHistory = [];
  updateStoredUser(storedUser);
  removeOrdersForUser(current.email);
  renderPurchaseHistory();
}

function initAccountInfo() {
  if (!requireAuth()) return;

  initAuthPage();
  const user = getCurrentUser();
  if (!user) return;

  const nameEl = document.getElementById('accountName');
  const emailEl = document.getElementById('accountEmail');
  const roleEl = document.getElementById('accountRole');
  const rutEl  = document.getElementById('accountRut');
  const introEl = document.getElementById('accountIntro');
  const historyTitleEl = document.getElementById('purchaseHistoryTitle');
  const historyButton = document.getElementById('clearHistoryButton');

  if (nameEl) nameEl.textContent = user.name;
  if (emailEl) emailEl.textContent = user.email;
  if (roleEl) roleEl.textContent = user.role === 'admin' ? 'Administrador' : 'Cliente';
  if (rutEl) rutEl.textContent = user.rut || 'No ingresado';
  if (introEl) {
    introEl.textContent = user.role === 'admin'
      ? 'Administra el estado de los pedidos y revisa el detalle de cada compra.'
      : 'Revisa tu información, consulta el seguimiento de tus pedidos y cierra sesión cuando quieras.';
  }
  if (historyTitleEl) {
    historyTitleEl.textContent = user.role === 'admin' ? 'Pedidos asociados a tu cuenta' : 'Mis pedidos';
  }
  if (historyButton) {
    historyButton.hidden = user.role === 'admin';
  }

  renderPurchaseHistory();
  renderAdminOrders();
}

function addAuthStyles() {
  const style = document.createElement('style');
  style.textContent = `
    .header-user-name {
      font-size: 0.95rem;
      font-weight: 700;
      color: #4a3f35;
      margin-left: 0.8rem;
      white-space: nowrap;
    }
    header div:last-child {
      display: flex;
      align-items: center;
      gap: 0.85rem;
    }
  `;
  document.head.appendChild(style);
}

if (typeof window !== 'undefined') {
  window.printOrderReceipt = printOrderReceipt;
  window.addEventListener('DOMContentLoaded', () => {
    addAuthStyles();
    initAuthPage();
  });
}
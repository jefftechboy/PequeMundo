  const TRACKING_STEPS = [
    { id: 'received', title: 'Pedido recibido', note: 'Confirmamos tu compra y registramos el pedido.' },
    { id: 'preparing', title: 'En preparación', note: 'Nuestro equipo está preparando tu pedido.' },
    { id: 'shipping', title: 'En camino', note: 'El pedido salió a reparto y va en ruta.' },
    { id: 'delivered', title: 'Entregado', note: 'El pedido llegó a destino correctamente.' }
  ];

  function escapeHtml(value) {
    return String(value || '').replace(/[&<>\"]/g, char => ({
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;'
    }[char] || char));
  }

  function getOrderIdFromUrl() {
    const params = new URLSearchParams(window.location.search);
    return params.get('id');
  }

  function resolveOrder() {
    const requestedId = getOrderIdFromUrl();
    if (requestedId && typeof findOrderById === 'function') {
      const requestedOrder = findOrderById(requestedId);
      if (requestedOrder) return requestedOrder;
    }

    const lastOrderRaw = localStorage.getItem('pequemundo_ultimo_pedido');
    if (lastOrderRaw) {
      try {
        const lastOrder = JSON.parse(lastOrderRaw);
        if (lastOrder.id && typeof findOrderById === 'function') {
          return findOrderById(lastOrder.id) || ensureOrderShape(lastOrder);
        }
        return ensureOrderShape(lastOrder);
      } catch (error) {
        return null;
      }
    }

    if (typeof getCurrentUserPurchases === 'function') {
      const orders = getCurrentUserPurchases();
      return orders.length > 0 ? orders[0] : null;
    }

    return null;
  }

  function renderOrderItems(order) {
    const container = document.getElementById('orderItems');
    container.innerHTML = order.items.map(item => `
      <div class="order-item">
        <div>
          <div class="order-item-name">${escapeHtml(item.nombre)}</div>
          <div class="order-item-qty">Cantidad: ${item.cantidad}</div>
        </div>
        <div class="order-item-price">${formatPrice(item.precio * item.cantidad)}</div>
      </div>
    `).join('');
  }

  function renderSteps(order) {
    const container = document.getElementById('trackingSteps');
    const currentMeta = getOrderStatusMeta(order.status);
    container.innerHTML = TRACKING_STEPS.map(step => {
      const meta = getOrderStatusMeta(step.id);
      const stateClass = meta.step < currentMeta.step
        ? 'completed'
        : meta.step === currentMeta.step
          ? 'active'
          : '';
      return `
        <div class="step ${stateClass}">
          <div class="step-icon"><i class="fas ${meta.icon}"></i></div>
          <div>
            <div class="step-title">${step.title}</div>
            <div class="step-note">${step.note}</div>
          </div>
        </div>
      `;
    }).join('');
  }

  function renderHistory(order) {
    const container = document.getElementById('statusHistory');
    container.innerHTML = order.statusHistory.slice().reverse().map(entry => {
      const meta = getOrderStatusMeta(entry.status);
      return `
        <div class="history-row">
          <div>
            <strong>${meta.label}</strong>
            <span>${entry.note || meta.description}</span>
          </div>
          <span>${formatOrderDateTime(entry.date)}</span>
        </div>
      `;
    }).join('');
  }

  function renderOrder(order) {
    const meta = getOrderStatusMeta(order.status);
    const deliveryType = order.deliveryType === 'pickup' ? 'Retiro en tienda' : 'Despacho a domicilio';
    const regionLabel = order.deliveryType === 'pickup'
      ? 'No aplica'
      : (order.shippingRegion === 'otra' ? 'Otras regiones' : 'Región Metropolitana');
    const address = order.deliveryType === 'pickup'
      ? 'No aplica (retiro en tienda)'
      : (order.shippingAddress || 'Dirección no informada');

    document.getElementById('orderId').textContent = order.id;
    document.getElementById('orderCustomer').textContent = order.customerName || 'Cliente PequeMundo';
    document.getElementById('orderDeliveryType').textContent = deliveryType;
    document.getElementById('orderAddress').textContent = `${address} · ${regionLabel}`;
    document.getElementById('orderDate').textContent = formatOrderDateTime(order.createdAt);
    document.getElementById('orderTotal').textContent = formatPrice(order.total);
    document.getElementById('heroDescription').textContent = `Pedido generado el ${formatOrderDate(order.createdAt)}. Puedes compartir este número con soporte si lo necesitas.`;
    document.getElementById('trackingMessage').textContent = meta.description;

    const statusBadge = document.getElementById('orderStatusBadge');
    statusBadge.className = `status-pill status-${meta.id}`;
    statusBadge.innerHTML = `<i class="fas ${meta.icon}"></i> ${meta.shortLabel}`;

    renderOrderItems(order);
    renderSteps(order);
    renderHistory(order);

    const receiptButton = document.getElementById('receiptButton');
    if (receiptButton) {
      receiptButton.onclick = () => {
        if (typeof printOrderReceipt === 'function') {
          printOrderReceipt(order.id);
        } else {
          alert('No se pudo generar la boleta.');
        }
      };
    }

    document.getElementById('emptyState').hidden = true;
    document.getElementById('orderView').hidden = false;
  }

  window.addEventListener('DOMContentLoaded', () => {
    if (typeof initAuthPage === 'function') {
      initAuthPage();
    }

    const order = resolveOrder();
    if (!order) {
      document.getElementById('emptyState').hidden = false;
      document.getElementById('orderView').hidden = true;
      return;
    }

    renderOrder(order);
  });

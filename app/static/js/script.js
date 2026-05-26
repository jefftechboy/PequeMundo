// Cargar carrito desde localStorage
let carrito = JSON.parse(localStorage.getItem("carrito")) || [];

// Guardar carrito
function guardarCarrito() {
    localStorage.setItem("carrito", JSON.stringify(carrito));
}

// Agregar producto
function agregarCarrito(nombre, precio) {
    carrito.push({ nombre, precio });
    guardarCarrito();
    alert(nombre + " agregado al carrito 🛒");
}

// Mostrar carrito
function mostrarCarrito() {
    let lista = document.getElementById("listaCarrito");
    let total = 0;

    lista.innerHTML = "";

    carrito.forEach((item, index) => {
        let li = document.createElement("li");
        li.textContent = item.nombre + " - $" + item.precio;

        let btn = document.createElement("button");
        btn.textContent = "❌";
        btn.onclick = () => eliminarProducto(index);

        li.appendChild(btn);
        lista.appendChild(li);

        total += item.precio;
    });

    document.getElementById("total").textContent = "Total: $" + total;
}

// Eliminar producto
function eliminarProducto(index) {
    carrito.splice(index, 1);
    guardarCarrito();
    mostrarCarrito();
}

// Simular compra
function comprar() {
    if (carrito.length === 0) {
        alert("Carrito vacío ❌");
        return;
    }

    carrito = [];
    guardarCarrito();

    alert("Compra realizada con éxito ✅");
    window.location.href = "pedido.html";
}
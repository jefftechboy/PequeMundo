// Simulación API de pago tipo MercadoPago

function procesarPago() {
    let carrito = JSON.parse(localStorage.getItem("carrito")) || [];

    if (carrito.length === 0) {
        alert("Carrito vacío ❌");
        return;
    }

    let total = carrito.reduce((sum, item) => sum + item.precio, 0);

    let datosPago = {
        monto: total,
        moneda: "CLP",
        items: carrito
    };

    console.log("Enviando a API...", datosPago);

    // Simulación llamada API
    setTimeout(() => {
        let respuesta = {
            status: "approved",
            id_pago: Math.floor(Math.random() * 1000000)
        };

        if (respuesta.status === "approved") {
            alert("Pago aprobado ✅ ID: " + respuesta.id_pago);

            localStorage.removeItem("carrito");

            window.location.href = "pedido.html";
        } else {
            alert("Pago rechazado ❌");
        }

    }, 2000); // simula delay de API
}
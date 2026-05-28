function mostrarAlerta(event) {

    event.preventDefault();

    let form = event.target.form;

    let cantidad = form.querySelector('input[name="cantidad"]');

    // VALIDAR SI ES 0
    if(parseInt(cantidad.value) <= 0){

        Swal.fire({
            icon: 'warning',
            title: 'Cantidad inválida',
            text: 'Debes seleccionar al menos 1 producto'
        });

        return;
    }

    // CONFIRMACION
    Swal.fire({
        title: '¿Confirmar compra?',
        icon: 'question',
        showCancelButton: true,
        confirmButtonText: 'Sí, comprar',
        cancelButtonText: 'Cancelar'
    }).then((result) => {

        if (result.isConfirmed) {

            form.submit();

        }

    });

}


function confirmar_compra_carrito(event) {

    event.preventDefault();

    Swal.fire({
        title: '¿Confirmar compra?',
        text: 'Iras a la pagina de pago',
        icon: 'question',
        showCancelButton: true,
        confirmButtonText: 'Sí, confirmar',
        cancelButtonText: 'Cancelar'
    }).then((result) => {

        if (result.isConfirmed) {

            event.target.form.submit();

        }

    });

}
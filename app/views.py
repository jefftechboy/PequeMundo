import json
from functools import wraps

import mercadopago

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User, Group
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from .forms import *

# Decorador para verificar si es administrador
def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, 'Debe iniciar sesion')
            return redirect('IDpaginalogin')
        if not request.user.is_staff:
            messages.error(request, 'Solo los administradores pueden acceder a esta pagina')
            return redirect('IDindex')
        return view_func(request, *args, **kwargs)
    return wrapper


# Create your views here.
def index(request):
    return render(request, 'menu.html')


# Create your views here.
def paginaProductos(request):
    return render(request, 'productos.html')


def paginaProductos(request):

    datosMuebles = mueble.objects.all()

    page = request.GET('page',1)
    try:
        pass
        paginator = Paginator(datosMuebles,5)
        muebles = paginator.page(page)
    except:
        pass 


    # pagina actual

    datos = {
        'entity': datosMuebles,
        'paginator': paginator
    }

    return render(
        request,
        'productos.html',
        datos
    )

def paginaCarrito(request):

    carritoCompra = request.session.get('carritoCompra', {})
    muebles = mueble.objects.all()
    datos = {
        "productosCarrito":carritoCompra,
        "muebles":muebles
    }
    return render(request, 'carrito.html', datos)
    
    


def paginaPedido(request):
    return render(request,'pedido.html')

def gestion_muebles(request):
    return render(request,'gestiones/administracion/vendedor/gestionMuebles.html')

# GESTION DE LOGIN USUARIOS
def paginaCrearCuenta(request):
    if request.method == 'POST':

        formulario = UserCreationForm(request.POST)

        if formulario.is_valid():

            formulario.save()
            
            user = authenticate(
                username=formulario.cleaned_data['username'],
                password=formulario.cleaned_data['password1']
            )
            # obtener grupo
            grupo = Group.objects.get(name='clientes')

            # agregar usuario al grupo
            user.groups.add(grupo)
            if user is not None:
                login(request, user)

            return render(request, 'menu.html')

    else:
        formulario = UserCreationForm()

    datos = {
        'formulario_de_usuario': formulario
    }

    return render(request, 'crearCuenta.html', datos)

def paginaLogin(request):

    if request.method == 'POST':

        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        # Validar que los campos no estén vacíos
        if not username or not password:
            return render(request, 'login/login.html', {
                'error': 'Por favor completa todos los campos'
            })

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)
            messages.success(request, f'¡Bienvenido {user.username}!')
            return redirect('IDindex')

        else:
            return render(request, 'login/login.html', {
                'error': 'Usuario o contraseña incorrectos'
            })

    return render(request,'login/login.html')

def cerrarSesion(request):
    logout(request)
    return render(request,'menu.html')

# GESTION DE PERFIL DE USUARIO (CLIENTE)
def paginaPerfilCliente(request):
    
    # Verificar si el usuario está autenticado
    if not request.user.is_authenticated:
        messages.warning(request, 'Debe iniciar sesión para ver su perfil')
        return redirect('IDpaginalogin')
    
    existe = cuenta.objects.filter(
        usuario_cuenta=request.user.id
    ).exists()
    if existe:
        perfil = cuenta.objects.get(
            usuario_cuenta=request.user.id
        )

        varDatosPerfilCliente = {
            'cuentaCliente': perfil
        } 
        return render(request,'cliente/perfilCliente.html',varDatosPerfilCliente)
    else:
        datos = {
            'formularioPerfilCliente' : perfilClienteform(),
            'comuna' : comuna.objects.all(),
        }
        if request.method == 'POST':

            formulario = perfilClienteform(request.POST)

            if formulario.is_valid():

                formulario.save()

                return redirect('IDpaginaPerfilCliente')
        return render(request,'cliente/perfilCliente.html',datos)


def actualizarPerfilCliente(request, id):

    clienteDatos = cuenta.objects.get(id=id)

    comunas = comuna.objects.all()

    datos = {
        'formularioCliente': perfilClienteform(instance=clienteDatos),
        'cuentaCliente': clienteDatos,
        'comuna': comunas,
    }

    if request.method == 'POST':

        formulario = perfilClienteform(
            request.POST,
            instance=clienteDatos
        )
        if formulario.is_valid():

            formulario.save()

            return redirect('IDpaginaPerfilCliente')

    return render(
        request,
        'cliente/actualizarPerfilCliente.html',
        datos
    )
# CATALOGO

def listarCatalogo(request):
    # TODOS LOS MUEBLES
    muebles = mueble.objects.all()

    # PAGINA ACTUAL
    page = request.GET.get('page', 1)

    # PAGINADOR
    paginator = Paginator(muebles, 8)

    try:

        muebles = paginator.page(page)

    except:

        muebles = paginator.page(1)

    # CONTEXTO
    varDatosMuebles = {

        'entity': muebles,

        'paginator': paginator,

        'datosMuebles': muebles
    }

    return render(
        request,
        'productos.html',
        varDatosMuebles
    )


def agregar_carrito(request, id):

    if request.method == "POST":

        try:
            producto = mueble.objects.get(id=id)
        except mueble.DoesNotExist:
            messages.error(request, 'El producto no existe')
            return redirect('IDpaginaProductos')

        try:
            cantidad = int(request.POST.get('cantidad'))
        except (ValueError, TypeError):
            messages.error(request, 'Cantidad inválida')
            return redirect('IDpaginaProductos')

        carritoCompra = request.session.get('carritoCompra', {})

        producto_id = str(producto.id)

        if producto_id in carritoCompra:
            carritoCompra[producto_id] += cantidad
        else:
            carritoCompra[producto_id] = cantidad

        request.session['carritoCompra'] = carritoCompra
        request.session.modified = True

        return render(request, 'carrito.html', {
            'productosCarrito': carritoCompra
        })

    return redirect('IDpaginaProductos')
# ------------------------------------------------------------------
def eliminar_item_carrito(request, id):

    try:
        detalle = detalleCompra.objects.get(idDetalle=id)
    except detalleCompra.DoesNotExist:
        messages.error(request, 'El producto no existe en el carrito')
        return redirect('ver_carrito')

    carrito = detalle.idCompra

    # ELIMINAR SUBTOTAL DEL TOTAL
    carrito.total -= detalle.subtotal

    if carrito.total < 0:

        carrito.total = 0

    carrito.save()

    # ELIMINAR ITEM
    detalle.delete()

    messages.success(
        request,
        'Producto eliminado del carrito'
    )

    return redirect('ver_carrito')

def finalizar_compra(request):

    if request.method == "POST":

        # Verificar si el usuario está autenticado
        if not request.user.is_authenticated:
            messages.warning(request, 'Debe iniciar sesión para finalizar la compra')
            return redirect('IDpaginalogin')

        # OBTENER ID CARRITO
        carrito_id = request.session.get(
            'carrito_id'
        )

        if not carrito_id:

            return redirect('ver_carrito')

        # BUSCAR CARRITO
        carrito = compra.objects.get(
            idCompra=carrito_id
        )

        # BUSCAR CLIENTE
        try:
            cliente = cuenta.objects.get(
                usuario_cuenta=request.user.id
            )
        except cuenta.DoesNotExist:
            messages.error(request, 'Por favor completa tu perfil de cliente para finalizar la compra')
            return redirect('IDpaginaPerfilCliente')

        # ASIGNAR CLIENTE
        carrito.idCliente = cliente

        # FINALIZAR COMPRA
        carrito.completada = True

        # RESTAR STOCK
        for detalle in carrito.detalles.all():

            producto = detalle.idMueble

            producto.cantidad -= detalle.cantidad
            # SI NO QUEDA STOCK
            if producto.cantidad <= 0:

                producto.cantidad = 0

                producto.disponiblidad = disponiblidadMueble.objects.get(id=2)


            producto.save()

        # GUARDAR
        carrito.save()

        # BORRAR SESSION
        del request.session['carrito_id']
        messages.success(request,"Producto comprado")

    return redirect('IDhistorial_compras',carritoCompra)

# HISTORIAL DE PEDIDOS DEL CLIENTE
def historial_compras(request):
    compras = compra.objects.all()
    detalleCompras = detalleCompra.objects.all()
    datos = {
        'comprasCliente' : compras,
        'detallesComprasCliente' : detalleCompras,
    }
    return render(request,'pedido.html',datos)



# GESTIONES
@admin_required
def paginaInicioGestiones(request):
    # OBTENER EL MUEBLE MAS COMPRADO
    acumulado = {}
    vestasMuebles = {}
    detalleComprasTotales = detalleCompra.objects.all()
    comprasTotales = compra.objects.all()
    mueblesTotales = mueble.objects.all()

    for x in detalleComprasTotales:

        id_mueble = x.idMueble

        #cantidad
        if id_mueble in acumulado:
            acumulado[id_mueble] += x.cantidad
        else:
            acumulado[id_mueble] = x.cantidad
        #ventas totales
        if id_mueble in vestasMuebles:
            vestasMuebles[id_mueble.categoria_mueble.descripcion] += x.subtotal
        else:
            vestasMuebles[id_mueble.categoria_mueble.descripcion] = x.subtotal


    mayor_id = max(acumulado, key=acumulado.get)
    muebleMasVendido = mueble.objects.get(nombre=mayor_id)
    mayor_cantidad = acumulado[mayor_id]


    # CANTIDAD DE MUEBLES + STOCK/NO DISPONIBLES
    v_contador_de_muebles = 0
    v_contador_de_muebles_Stock = 0
    v_contador_de_muebles_sinStock = 0
    for x in mueblesTotales:    
        v_contador_de_muebles +=1
        if (x.disponiblidad.descripcion == 'No disponible' ):
            v_contador_de_muebles_sinStock += 1
        else:
            v_contador_de_muebles_Stock +=1

    # TOTAL DE INGRESOS
    v_totalIngresos = 0
    for c in comprasTotales:
        v_totalIngresos = v_totalIngresos + c.total
        


    datos = {
        'detallesCompras': detalleComprasTotales,
        'compras': comprasTotales,
        'muebles': mueblesTotales,
        'mueble_mas_vendido' : muebleMasVendido,
        'mueble_mas_vendido_cantidad' : mayor_cantidad,
        # CANTIDAD MUEBLES/STOCK/SIN STOCK
        'cantidad_muebles' : v_contador_de_muebles,
        'cantidad_muebles_stock' : v_contador_de_muebles_Stock,
        'cantidad_muebles_Sinstock' : v_contador_de_muebles_sinStock,
        # CANTIDAD DE INGRESOS
        'cantidad_ingresosTotales' : v_totalIngresos,
        # DICCIONARIO DE VENTAS TOTALES
        'ventas_muebles' :vestasMuebles,
    }

    return render(request,'gestiones/inicioGestiones.html',datos)






@admin_required
def paginaGestionMuebles(request):
    muebles = mueble.objects.all()
    datos = {
        'muebles':muebles,
    }
    return render(request,'gestiones/administracion/vendedor/gestionMuebles.html',datos)

@admin_required
def modificar_mueble(request, id):

    muebleDatos = mueble.objects.get(id=id)
    # SI ENVÍA FORMULARIO
    if request.method == 'POST':

        formulario = muebleForm(
            request.POST,
            request.FILES,
            instance=muebleDatos,
        )

        # VALIDAR
        if formulario.is_valid():

            formulario.save()

            return redirect(
                'IDpaginaGestionMuebles'
            )

    # SI SOLO ENTRA A LA PÁGINA
    else:

        formulario = muebleForm(
            instance=muebleDatos
        )

    # CONTEXTO
    datos = {

        'formularioMueble': formulario,
        'muebleDatos': muebleDatos,

    }

    return render(

        request,
        'gestiones/administracion/vendedor/editarMueble.html',
        datos

    )

@admin_required
def crearMueble(request):
    datos = {
            'formularioMueble' : muebleForm(),
        }
    if request.method == 'POST':

        formulario = muebleForm(request.POST,request.FILES)

        if formulario.is_valid():

            formulario.save()

            return redirect('IDpaginaGestionMuebles')
    return render(request,'gestiones/administracion/vendedor/crearMueble.html',datos)

@admin_required
def paginaGestionPedidos(request):
    return render(request,'gestiones/administracion/gestionPedidos.html')

# GESTION DE COMPRAS
@admin_required
def paginaGestionCompras(request):
    comprasTotales = compra.objects.all()
    detalleComprasTotales = detalleCompra.objects.all()
    datos = {
        'compras':comprasTotales,
        'detalleCompras':detalleComprasTotales,
    }
    return render(request,'gestiones/administracion/gestionPedidos.html',datos)


@admin_required
def actualizarPedidos(request,id):
    detalleComprado = detalleCompra.objects.get(idDetalle=id)
    formulario = detalleCompraForm(request.POST,instance=detalleComprado)
    estadosDeCompras = estadoProductoComprado.objects.all()
    # SI ENVÍA FORMULARIO
    if request.method == 'POST':
        
        if formulario.is_valid():

            formulario.save()

            return redirect(
                'IDpaginaGestionCompras'
            )
    # CONTEXTO
    datos = {
        'formularioDetalleCompra': formulario,
        'detalleCompra':detalleComprado,
        'estadosDeCompras':estadosDeCompras,
    }

    return render(

        request,
        'gestiones/administracion/actualizarPedidos.html',
        datos

    )

@admin_required
def paginaGestionUsuarios(request):
    usuarios = User.objects.all()

    datos = {
        'usuarios': usuarios
    }

    return render(request, 'gestiones/administracion/administrador/gestionUsuarios.html', datos)



# GESTION CREAR CUENTA
@admin_required
def paginaGestionCrearCuenta(request):
    datos = {
        'formularioCuenta' : perfilClienteform(),
        'formularioUser' : UserCreationForm(),

    }

    return render(request, 'gestiones/administracion/administrador/gestionCrearCuenta.html',datos)

def crear_preferencia_mp(request):

    carritoCompra = request.session.get('carritoCompra', {})

    if not carritoCompra:
        return redirect('ver_carrito')

    items = []

    for producto_id, cantidad in carritoCompra.items():

        try:
            producto = mueble.objects.get(id=producto_id)
        except mueble.DoesNotExist:
            continue

        items.append({
            "id": str(producto.id),
            "title": producto.nombre,
            "quantity": int(cantidad),
            "unit_price": float(producto.precio),
            "currency_id": "CLP",
        })

    if not items:
        return redirect('ver_carrito')

    sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)
    preference_data = {
        "items": items,
        "back_urls": {
            "success": "https://hedging-idly-eggplant.ngrok-free.dev/pago/exitoso/",
            "failure": "https://hedging-idly-eggplant.ngrok-free.dev/pago/fallido/",
            "pending": "https://hedging-idly-eggplant.ngrok-free.dev/pago/pendiente/",
        },
        "auto_return": "approved",
        "external_reference": str(request.user.id) if request.user.is_authenticated else "invitado",
    }
    print("PREFERENCE DATA:", preference_data)

    preference_response = sdk.preference().create(preference_data)

    print("STATUS:", preference_response.get("status"))
    print("RESPONSE:", preference_response.get("response"))

    preference = preference_response.get("response", {})

    init_point = preference.get("init_point") or preference.get("sandbox_init_point")

    if not init_point:
        error_msg = preference.get("message", "Error desconocido de MercadoPago")
        return HttpResponse(
            f"Error MP: {error_msg} | Respuesta completa: {preference}",
            status=500
        )

    return redirect(init_point)

def pago_exitoso(request):
    """MercadoPago redirige aquí cuando el pago es aprobado."""

    print("ENTRO A PAGO EXITOSO")
    print("SESSION:", dict(request.session.items()))

    carritoCompra = request.session.get('carritoCompra', {})

    print("CARRITO:", carritoCompra)

    if not carritoCompra:
        messages.error(request, "No hay productos en el carrito.")
        return redirect('ver_carrito')

    try:
        cliente = cuenta.objects.get(
            usuario_cuenta=request.user.id
        )
    except cuenta.DoesNotExist:
        messages.error(request, 'No se encontró el perfil del cliente.')
        return redirect('IDpaginaPerfilCliente')

    carrito = compra.objects.create(
        idCliente=cliente,
        total=0,
        completada=True
    )

    total = 0

    for producto_id, cantidad in carritoCompra.items():

        try:
            producto = mueble.objects.get(id=producto_id)
        except mueble.DoesNotExist:
            continue

        cantidad = int(cantidad)
        subtotal = producto.precio * cantidad

        detalleCompra.objects.create(
            idCompra=carrito,
            idMueble=producto,
            cantidad=cantidad,
            subtotal=subtotal
        )

        total += subtotal

        producto.cantidad -= cantidad

        if producto.cantidad <= 0:
            producto.cantidad = 0
            producto.disponiblidad = disponiblidadMueble.objects.get(id=2)

        producto.save()

    carrito.total = total
    carrito.save()

    request.session.pop('carritoCompra', None)
    request.session.modified = True

    print("COMPRA GUARDADA:", carrito.idCompra)
    print("CARRITO BORRADO:", request.session.get('carritoCompra'))

    messages.success(request, "¡Pago realizado con éxito!")
    return redirect('IDhistorial_compras')



def pago_fallido(request):
    messages.error(request, "El pago fue rechazado. Intenta nuevamente.")
    return redirect('ver_carrito')


def pago_pendiente(request):
    messages.warning(request, "Tu pago está pendiente de confirmación.")
    return redirect('IDhistorial_compras')


@csrf_exempt
def webhook_mp(request):
    """MercadoPago notifica aquí los cambios de estado de pago."""
    if request.method == "POST":
        data = json.loads(request.body)
        if data.get("type") == "payment":
            sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)
            payment_id = data["data"]["id"]
            payment_info = sdk.payment().get(payment_id)
            payment = payment_info["response"]

            if payment["status"] == "approved":
                external_ref = payment.get("external_reference")
                if external_ref:
                    try:
                        carrito = compra.objects.get(idCompra=int(external_ref))
                        if not carrito.completada:
                            carrito.completada = True
                            for detalle in carrito.detalles.all():
                                producto = detalle.idMueble
                                producto.cantidad -= detalle.cantidad
                                if producto.cantidad <= 0:
                                    producto.cantidad = 0
                                    producto.disponiblidad = disponiblidadMueble.objects.get(id=2)
                                producto.save()
                            carrito.save()
                    except compra.DoesNotExist:
                        pass

    return JsonResponse({"status": "ok"})
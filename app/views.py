import json
from .forms import *
from functools import wraps
import mercadopago
import requests
from django.utils import timezone
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User, Group
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
import threading











# Create your views here.
def index(request):
    return render(request, 'menu.html')




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

@login_required
@user_passes_test(lambda u: u.groups.filter(name__in=['clientes']).exists(),login_url='IDindex')
def paginaCarrito(request):

    carritoCompra = request.session.get('carritoCompra', {})
    muebles = mueble.objects.all()

    total = 0

    for id_producto, cantidad in carritoCompra.items():

        try:
            producto = mueble.objects.get(id=id_producto)
            total += producto.precio * cantidad
        except mueble.DoesNotExist:
            pass

    datos = {
        "productosCarrito": carritoCompra,
        "muebles": muebles,
        "total": total
    }

    return render(request, 'carrito.html', datos)
    
    

@login_required
@user_passes_test(lambda u: u.groups.filter(name__in=['clientes']).exists(),login_url='IDindex')
def paginaPedido(request):
    return render(request,'pedido.html')


# CREAR CUENTAS USERs
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
@login_required
@user_passes_test(
    lambda u: u.groups.filter( name__in=['clientes']).exists(),login_url='IDindex')
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

@login_required
@user_passes_test(lambda u: u.groups.filter( name__in=['clientes']).exists(),login_url='IDindex')
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

@login_required
@user_passes_test(lambda u: u.groups.filter( name__in=['clientes']).exists(),login_url='IDindex')
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

        return redirect('ver_carrito')

    return redirect('IDpaginaProductos')
# ------------------------------------------------------------------
@login_required
@user_passes_test(lambda u: u.groups.filter( name__in=['clientes']).exists(),login_url='IDindex')
def eliminar_item_carrito(request, id):

    carritoCompra = request.session.get('carritoCompra', {})

    producto_id = str(id)

    if producto_id in carritoCompra:

        del carritoCompra[producto_id]

        request.session['carritoCompra'] = carritoCompra
        request.session.modified = True

        messages.success(request, 'Producto eliminado del carrito')

    else:

        messages.error(request, 'El producto no existe en el carrito')

    return redirect('ver_carrito')
@login_required
@user_passes_test(lambda u: u.groups.filter( name__in=['clientes']).exists(),login_url='IDindex')
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

    return redirect('IDhistorial_compras')

# HISTORIAL DE PEDIDOS DEL CLIENTE
@login_required
@user_passes_test(lambda u: u.groups.filter( name__in=['clientes']).exists(),login_url='IDindex')
def historial_compras(request):
    compras = compra.objects.all().order_by('-fecha')
    print("lala")
    detalleCompras = detalleCompra.objects.all()
    for c in compras:
        print(c.idCompra)

    url = "https://6a18c0ad23c3626470abfd36.mockapi.io/api/pequeMundo/Envios"

    try:
        respuesta = requests.get(url, timeout=10)

        if respuesta.status_code == 200:
            envios = respuesta.json()
        else:
            envios = []

    except requests.RequestException:
        envios = []

    datos = {
        'comprasCliente': compras,
        'detallesComprasCliente': detalleCompras,
        'envios': envios,
    }
    return render(request, 'pedido.html', datos)


@login_required
@user_passes_test(lambda u: u.groups.filter(name__in=['admin', 'vendedores', 'finanzas']).exists(),login_url='IDindex')
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


@login_required
@user_passes_test(lambda u: u.groups.filter(name__in=['admin', 'vendedores', 'finanzas']).exists(),login_url='IDindex')
def paginaGestionMuebles(request):
    muebles = mueble.objects.all()
    datos = {
        'muebles':muebles,
    }
    return render(request,'gestiones/administracion/vendedor/gestionMuebles.html',datos)

@login_required
@user_passes_test(lambda u: u.groups.filter(name__in=['admin', 'vendedores', 'finanzas']).exists(),login_url='IDindex')
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
        'estados' : estadoMueble.objects.all(),
        'disponibilidades' : disponiblidadMueble.objects.all(),
        'categorias' : categoriaMueble.objects.all(),

    }

    return render(

        request,
        'gestiones/administracion/vendedor/editarMueble.html',
        datos

    )

@login_required
@user_passes_test(lambda u: u.groups.filter(name__in=['admin', 'vendedores', 'finanzas']).exists(),login_url='IDindex')
def crearMueble(request):
    datos = {
            'formularioMueble' : muebleForm(),
            'estados' : estadoMueble.objects.all(),
            'disponibilidades' : disponiblidadMueble.objects.all(),
            'categorias' : categoriaMueble.objects.all(),
        }
    if request.method == 'POST':

        formulario = muebleForm(request.POST,request.FILES)

        if formulario.is_valid():

            formulario.save()

            return redirect('IDpaginaGestionMuebles')
    return render(request,'gestiones/administracion/vendedor/crearMueble.html',datos)

@login_required
@user_passes_test(lambda u: u.groups.filter(name__in=['admin', 'vendedores', 'finanzas']).exists(),login_url='IDindex')
def paginaGestionPedidos(request):
    return render(request,'gestiones/administracion/gestionPedidos.html')

# GESTION DE COMPRAS
@login_required
@user_passes_test(lambda u: u.groups.filter(name__in=['admin', 'vendedores', 'finanzas']).exists(),login_url='IDindex')
def paginaGestionCompras(request):
    comprasTotales = compra.objects.all()
    detalleComprasTotales = detalleCompra.objects.all()
    datos = {
        'compras':comprasTotales,
        'detalleCompras':detalleComprasTotales,
    }
    return render(request,'gestiones/administracion/gestionPedidos.html',datos)


@login_required
@user_passes_test(lambda u: u.groups.filter(name__in=['admin', 'vendedores', 'finanzas']).exists(),login_url='IDindex')
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

@login_required
@user_passes_test(lambda u: u.groups.filter(name__in=['admin', 'vendedores', 'finanzas']).exists(),login_url='IDindex')
def paginaGestionUsuarios(request):
    usuarios = User.objects.all()

    datos = {
        'usuarios': usuarios
    }

    return render(request, 'gestiones/administracion/administrador/gestionUsuarios.html', datos)









@login_required
@user_passes_test(lambda u: u.groups.filter(name__in=['admin', 'vendedores', 'finanzas']).exists(),login_url='IDindex')
def paginaGestionCrearCuenta(request):
    if request.method == 'POST':

        formulario = UserCreationForm(request.POST)

        if formulario.is_valid():

            formulario.save()
            
            user = authenticate(
                username=formulario.cleaned_data['username'],
                password=formulario.cleaned_data['password1']
            )
            # obtener grupo
            grupo = Group.objects.get(name='Asignacion_Pendiente')

            # agregar usuario al grupo
            user.groups.add(grupo)
            return redirect("IDpaginaGestionUsuarios")

    else:
        formulario = UserCreationForm()

    datos = {
        'formulario_de_usuario': formulario
    }
    return render(request, 'gestiones/administracion/administrador/gestionCrearCuenta.html',datos)





















@login_required
@user_passes_test(lambda u: u.groups.filter(name__in=['clientes']).exists(),login_url='IDindex')
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



MOCKAPI_ENVIOS_URL = "https://6a18c0ad23c3626470abfd36.mockapi.io/api/pequeMundo/Envios"



def actualizar_estado_envio_mockapi(envio_id, nuevo_estado):
    url = f"{MOCKAPI_ENVIOS_URL}/{envio_id}"

    try:
        requests.patch(url, json={"EstadoEnvio": nuevo_estado}, timeout=10)
    except requests.RequestException as e:
        print("Error actualizando envio:", e)




def iniciar_actualizacion_envio(envio_id):
    threading.Timer(5, actualizar_estado_envio_mockapi, args=[envio_id, "Empaquetado"]).start()
    threading.Timer(10, actualizar_estado_envio_mockapi, args=[envio_id, "Preparado"]).start()
    threading.Timer(15, actualizar_estado_envio_mockapi, args=[envio_id, "En transito"]).start()

from django.utils import timezone
from zoneinfo import ZoneInfo
@login_required
@user_passes_test(lambda u: u.groups.filter(name__in=['clientes']).exists(),login_url='IDindex')
def pago_exitoso(request):
    """MercadoPago redirige aquí cuando el pago es aprobado."""

    carritoCompra = request.session.get('carritoCompra', {})

    if not carritoCompra:
        messages.error(request, "No hay productos en el carrito.")
        return redirect('ver_carrito')

    try:
        cliente = cuenta.objects.get(usuario_cuenta=request.user.id)
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
            producto = mueble.objects.get(pk=producto_id)
        except mueble.DoesNotExist:
            continue

        cantidad = int(cantidad)
        subtotal = producto.precio * cantidad

        detalle = detalleCompra.objects.create(
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
        fecha_chile = timezone.now().astimezone(
            ZoneInfo("America/Santiago")
        )
        data = {
            "DetalleCompra": detalle.pk,
            "Mueble": {
                "id": producto.pk,
                "nombre": producto.nombre,
                "precio": float(producto.precio),
                "cantidad": cantidad,
                "subtotal": float(subtotal),
            },
            "Direccion": cliente.direccion,
            "Cliente": cliente.nombre,
            "Telefono": cliente.telefono,
            "FechaEntrega": fecha_chile.isoformat(),            
            "EstadoEnvio": "Solicitado",
            "Compra": carrito.pk
        }

        try:
            respuesta = requests.post(MOCKAPI_ENVIOS_URL, json=data, timeout=10)

            if respuesta.status_code in [200, 201]:
                envio_creado = respuesta.json()
                envio_id = envio_creado.get("id")

                if envio_id:
                    iniciar_actualizacion_envio(envio_id)

        except requests.RequestException as e:
            print("Error enviando a MockAPI:", e)

        producto.save()

    carrito.total = total
    carrito.save()

    request.session.pop('carritoCompra', None)
    request.session.modified = True

    messages.success(request, "¡Pago realizado con éxito!")
    return redirect('IDhistorial_compras')



@login_required
@user_passes_test(lambda u: u.groups.filter(name__in=['clientes']).exists(),login_url='IDindex')
def pago_fallido(request):
    messages.error(request, "El pago fue rechazado. Intenta nuevamente.")
    return redirect('ver_carrito')


@login_required
@user_passes_test(lambda u: u.groups.filter(name__in=['clientes']).exists(),login_url='IDindex')
def pago_pendiente(request):
    messages.warning(request, "Tu pago está pendiente de confirmación.")
    return redirect('IDhistorial_compras')


@csrf_exempt
@login_required
@user_passes_test(lambda u: u.groups.filter(name__in=['clientes']).exists(),login_url='IDindex')
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


# GESTIÓN DE COMUNAS
@login_required
@user_passes_test(lambda u: u.groups.filter(name__in=['admin', 'vendedores', 'finanzas']).exists(),login_url='IDindex')
def paginaGestionComunas(request):
    comunas_list = comuna.objects.all()
    
    datos = {
        'comunas': comunas_list
    }
    
    return render(request, 'gestiones/administracion/administrador/gestionComunas.html', datos)


@login_required
@user_passes_test(lambda u: u.groups.filter(name__in=['admin', 'vendedores', 'finanzas']).exists(),login_url='IDindex')
def paginaGestionCrearComuna(request):
    if request.method == 'POST':
        descripcion = request.POST.get('descripcion')
        if descripcion:
            nueva_comuna = comuna(descripcion=descripcion)
            nueva_comuna.save()
            messages.success(request, 'Comuna creada exitosamente.')
            return redirect('IDpaginaGestionComunas')
        else:
            messages.error(request, 'Por favor, completa todos los campos.')
    
    return render(request, 'gestiones/administracion/administrador/gestionCrearComuna.html')


@login_required
@user_passes_test(lambda u: u.groups.filter(name__in=['admin', 'vendedores', 'finanzas']).exists(),login_url='IDindex')
def paginaGestionEditarComuna(request, id):
    try:
        comuna_obj = comuna.objects.get(id=id)
    except comuna.DoesNotExist:
        messages.error(request, 'La comuna no existe.')
        return redirect('IDpaginaGestionComunas')
    
    if request.method == 'POST':
        descripcion = request.POST.get('descripcion')
        if descripcion:
            comuna_obj.descripcion = descripcion
            comuna_obj.save()
            messages.success(request, 'Comuna actualizada exitosamente.')
            return redirect('IDpaginaGestionComunas')
        else:
            messages.error(request, 'Por favor, completa todos los campos.')
    
    datos = {
        'comuna': comuna_obj
    }
    
    return render(request, 'gestiones/administracion/administrador/gestionEditarComuna.html', datos)


@login_required
@user_passes_test(lambda u: u.groups.filter(name__in=['admin', 'vendedores', 'finanzas']).exists(),login_url='IDindex')
def paginaGestionEliminarComuna(request, id):
    try:
        comuna_obj = comuna.objects.get(id=id)
        comuna_obj.delete()
        messages.success(request, 'Comuna eliminada exitosamente.')
    except comuna.DoesNotExist:
        messages.error(request, 'La comuna no existe.')
    
    return redirect('IDpaginaGestionComunas')


# GESTIÓN DE TIPOS DE ENVÍO
@login_required
@user_passes_test(lambda u: u.groups.filter(name__in=['admin', 'vendedores', 'finanzas']).exists(),login_url='IDindex')
def paginaGestionTiposEnvio(request):
    tipos_envio_list = tipoEnvio.objects.all()
    
    datos = {
        'tipos_envio': tipos_envio_list
    }
    
    return render(request, 'gestiones/administracion/administrador/gestionTiposEnvio.html', datos)


@login_required
@user_passes_test(lambda u: u.groups.filter(name__in=['admin', 'vendedores', 'finanzas']).exists(),login_url='IDindex')
def paginaGestionCrearTipoEnvio(request):
    if request.method == 'POST':
        descripcion = request.POST.get('descripcion')
        if descripcion:
            nuevo_tipo_envio = tipoEnvio(descripcion=descripcion)
            nuevo_tipo_envio.save()
            messages.success(request, 'Tipo de envío creado exitosamente.')
            return redirect('IDpaginaGestionTiposEnvio')
        else:
            messages.error(request, 'Por favor, completa todos los campos.')
    
    return render(request, 'gestiones/administracion/administrador/gestionCrearTipoEnvio.html')


@login_required
@user_passes_test(lambda u: u.groups.filter(name__in=['admin', 'vendedores', 'finanzas']).exists(),login_url='IDindex')
def paginaGestionEditarTipoEnvio(request, id):
    try:
        tipo_envio_obj = tipoEnvio.objects.get(id=id)
    except tipoEnvio.DoesNotExist:
        messages.error(request, 'El tipo de envío no existe.')
        return redirect('IDpaginaGestionTiposEnvio')
    
    if request.method == 'POST':
        descripcion = request.POST.get('descripcion')
        if descripcion:
            tipo_envio_obj.descripcion = descripcion
            tipo_envio_obj.save()
            messages.success(request, 'Tipo de envío actualizado exitosamente.')
            return redirect('IDpaginaGestionTiposEnvio')
        else:
            messages.error(request, 'Por favor, completa todos los campos.')
    
    datos = {
        'tipo_envio': tipo_envio_obj
    }
    
    return render(request, 'gestiones/administracion/administrador/gestionEditarTipoEnvio.html', datos)


# GESTIÓN DE TIPOS DE CUENTA
@login_required
@user_passes_test(lambda u: u.groups.filter(name__in=['admin', 'vendedores', 'finanzas']).exists(),login_url='IDindex')
def paginaGestionTiposCuenta(request):
    tipos_cuenta_list = tipoCuenta.objects.all()
    
    datos = {
        'tipos_cuenta': tipos_cuenta_list
    }
    
    return render(request, 'gestiones/administracion/administrador/gestionTiposCuenta.html', datos)


@login_required
@user_passes_test(lambda u: u.groups.filter(name__in=['admin', 'vendedores', 'finanzas']).exists(),login_url='IDindex')
def paginaGestionCrearTipoCuenta(request):
    if request.method == 'POST':
        descripcion = request.POST.get('descripcion')
        if descripcion:
            nuevo_tipo_cuenta = tipoCuenta(descripcion=descripcion)
            nuevo_tipo_cuenta.save()
            messages.success(request, 'Tipo de cuenta creado exitosamente.')
            return redirect('IDpaginaGestionTiposCuenta')
        else:
            messages.error(request, 'Por favor, completa todos los campos.')
    
    return render(request, 'gestiones/administracion/administrador/gestionCrearTipoCuenta.html')


@login_required
@user_passes_test(lambda u: u.groups.filter(name__in=['admin', 'vendedores', 'finanzas']).exists(),login_url='IDindex')
def paginaGestionEditarTipoCuenta(request, id):
    try:
        tipo_cuenta_obj = tipoCuenta.objects.get(id=id)
    except tipoCuenta.DoesNotExist:
        messages.error(request, 'El tipo de cuenta no existe.')
        return redirect('IDpaginaGestionTiposCuenta')
    
    if request.method == 'POST':
        descripcion = request.POST.get('descripcion')
        if descripcion:
            tipo_cuenta_obj.descripcion = descripcion
            tipo_cuenta_obj.save()
            messages.success(request, 'Tipo de cuenta actualizado exitosamente.')
            return redirect('IDpaginaGestionTiposCuenta')
        else:
            messages.error(request, 'Por favor, completa todos los campos.')
    
    datos = {
        'tipo_cuenta': tipo_cuenta_obj
    }
    
    return render(request, 'gestiones/administracion/administrador/gestionEditarTipoCuenta.html', datos)


@login_required
@user_passes_test(lambda u: u.groups.filter(name__in=['admin', 'vendedores', 'finanzas']).exists(),login_url='IDindex')
def paginaGestionEliminarTipoCuenta(request, id):
    try:
        tipo_cuenta_obj = tipoCuenta.objects.get(id=id)
        tipo_cuenta_obj.delete()
        messages.success(request, 'Tipo de cuenta eliminado exitosamente.')
    except tipoCuenta.DoesNotExist:
        messages.error(request, 'El tipo de cuenta no existe.')
    
    return redirect('IDpaginaGestionTiposCuenta')


# GESTIÓN DE PERFILES DE USUARIOS
@login_required
@user_passes_test(lambda u: u.groups.filter(name__in=['admin', 'vendedores', 'finanzas']).exists(),login_url='IDindex')
def paginaGestionPerfiles(request):
    perfiles_list = Group.objects.all()
    
    datos = {
        'perfiles': perfiles_list
    }
    
    return render(request, 'gestiones/administracion/administrador/gestionPerfiles.html', datos)


@login_required
@user_passes_test(lambda u: u.groups.filter(name__in=['admin', 'vendedores', 'finanzas']).exists(),login_url='IDindex')
def paginaGestionCrearPerfil(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        if nombre:
            nuevo_perfil = Group(name=nombre)
            nuevo_perfil.save()
            messages.success(request, 'Perfil de usuario creado exitosamente.')
            return redirect('IDpaginaGestionPerfiles')
        else:
            messages.error(request, 'Por favor, completa todos los campos.')
    
    return render(request, 'gestiones/administracion/administrador/gestionCrearPerfil.html')


@login_required
@user_passes_test(lambda u: u.groups.filter(name__in=['admin', 'vendedores', 'finanzas']).exists(),login_url='IDindex')
def paginaGestionEditarPerfil(request, id):
    try:
        perfil_obj = Group.objects.get(id=id)
    except Group.DoesNotExist:
        messages.error(request, 'El perfil no existe.')
        return redirect('IDpaginaGestionPerfiles')
    
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        if nombre:
            perfil_obj.name = nombre
            perfil_obj.save()
            messages.success(request, 'Perfil actualizado exitosamente.')
            return redirect('IDpaginaGestionPerfiles')
        else:
            messages.error(request, 'Por favor, completa todos los campos.')
    
    datos = {
        'perfil': perfil_obj
    }
    
    return render(request, 'gestiones/administracion/administrador/gestionEditarPerfil.html', datos)


@login_required
@user_passes_test(lambda u: u.groups.filter(name__in=['admin', 'vendedores', 'finanzas']).exists(),login_url='IDindex')
def paginaGestionEliminarPerfil(request, id):
    try:
        perfil_obj = Group.objects.get(id=id)
        perfil_obj.delete()
        messages.success(request, 'Perfil eliminado exitosamente.')
    except Group.DoesNotExist:
        messages.error(request, 'El perfil no existe.')
    
    return redirect('IDpaginaGestionPerfiles')


# GESTIÓN DE DISPONIBILIDADES
@login_required
@user_passes_test(lambda u: u.groups.filter(name__in=['admin', 'vendedores', 'finanzas']).exists(),login_url='IDindex')
def paginaGestionDisponibilidades(request):
    disponibilidades_list = disponiblidadMueble.objects.all()
    
    datos = {
        'disponibilidades': disponibilidades_list
    }
    
    return render(request, 'gestiones/administracion/administrador/gestionDisponibilidades.html', datos)


@login_required
@user_passes_test(lambda u: u.groups.filter(name__in=['admin', 'vendedores', 'finanzas']).exists(),login_url='IDindex')
def paginaGestionCrearDisponibilidad(request):
    if request.method == 'POST':
        descripcion = request.POST.get('descripcion')
        if descripcion:
            nueva_disponibilidad = disponiblidadMueble(descripcion=descripcion)
            nueva_disponibilidad.save()
            messages.success(request, 'Disponibilidad creada exitosamente.')
            return redirect('IDpaginaGestionDisponibilidades')
        else:
            messages.error(request, 'Por favor, completa todos los campos.')
    
    return render(request, 'gestiones/administracion/administrador/gestionCrearDisponibilidad.html')


@login_required
@user_passes_test(lambda u: u.groups.filter(name__in=['admin', 'vendedores', 'finanzas']).exists(),login_url='IDindex')
def paginaGestionEditarDisponibilidad(request, id):
    try:
        disponibilidad_obj = disponiblidadMueble.objects.get(id=id)
    except disponiblidadMueble.DoesNotExist:
        messages.error(request, 'La disponibilidad no existe.')
        return redirect('IDpaginaGestionDisponibilidades')
    
    if request.method == 'POST':
        descripcion = request.POST.get('descripcion')
        if descripcion:
            disponibilidad_obj.descripcion = descripcion
            disponibilidad_obj.save()
            messages.success(request, 'Disponibilidad actualizada exitosamente.')
            return redirect('IDpaginaGestionDisponibilidades')
        else:
            messages.error(request, 'Por favor, completa todos los campos.')
    
    datos = {
        'disponibilidad': disponibilidad_obj
    }
    
    return render(request, 'gestiones/administracion/administrador/gestionEditarDisponibilidad.html', datos)


@login_required
@user_passes_test(lambda u: u.groups.filter(name__in=['admin', 'vendedores', 'finanzas']).exists(),login_url='IDindex')
def paginaGestionEliminarDisponibilidad(request, id):
    try:
        disponibilidad_obj = disponiblidadMueble.objects.get(id=id)
        disponibilidad_obj.delete()
        messages.success(request, 'Disponibilidad eliminada exitosamente.')
    except disponiblidadMueble.DoesNotExist:
        messages.error(request, 'La disponibilidad no existe.')
    
    return redirect('IDpaginaGestionDisponibilidades')


# GESTIÓN DE CATEGORÍAS DE MUEBLES
@login_required
@user_passes_test(lambda u: u.groups.filter(name__in=['admin', 'vendedores', 'finanzas']).exists(),login_url='IDindex')
def paginaGestionCategoriasMuebles(request):
    categorias_list = categoriaMueble.objects.all()
    
    datos = {
        'categorias': categorias_list
    }
    
    return render(request, 'gestiones/administracion/administrador/gestionCategoriasMuebles.html', datos)

@login_required
@user_passes_test(lambda u: u.groups.filter(name__in=['admin', 'vendedores', 'finanzas']).exists(),login_url='IDindex')
def paginaGestionCrearCategoriaMueble(request):
    if request.method == 'POST':
        descripcion = request.POST.get('descripcion')
        if descripcion:
            nueva_categoria = categoriaMueble(descripcion=descripcion)
            nueva_categoria.save()
            messages.success(request, 'Categoría de mueble creada exitosamente.')
            return redirect('IDpaginaGestionCategoriasMuebles')
        else:
            messages.error(request, 'Por favor, completa todos los campos.')
    
    return render(request, 'gestiones/administracion/administrador/gestionCrearCategoriaMueble.html')

@login_required
@user_passes_test(lambda u: u.groups.filter(name__in=['admin', 'vendedores', 'finanzas']).exists(),login_url='IDindex')
def paginaGestionEditarCategoriaMueble(request, id):
    try:
        categoria_obj = categoriaMueble.objects.get(id=id)
    except categoriaMueble.DoesNotExist:
        messages.error(request, 'La categoría no existe.')
        return redirect('IDpaginaGestionCategoriasMuebles')
    
    if request.method == 'POST':
        descripcion = request.POST.get('descripcion')
        if descripcion:
            categoria_obj.descripcion = descripcion
            categoria_obj.save()
            messages.success(request, 'Categoría actualizada exitosamente.')
            return redirect('IDpaginaGestionCategoriasMuebles')
        else:
            messages.error(request, 'Por favor, completa todos los campos.')
    
    datos = {
        'categoria': categoria_obj
    }
    
    return render(request, 'gestiones/administracion/administrador/gestionEditarCategoriaMueble.html', datos)


@login_required
@user_passes_test(lambda u: u.groups.filter(name__in=['admin', 'vendedores', 'finanzas']).exists(),login_url='IDindex')
def paginaGestionEliminarCategoriaMueble(request, id):
    try:
        categoria_obj = categoriaMueble.objects.get(id=id)
        categoria_obj.delete()
        messages.success(request, 'Categoría eliminada exitosamente.')
    except categoriaMueble.DoesNotExist:
        messages.error(request, 'La categoría no existe.')
    
    return redirect('IDpaginaGestionCategoriasMuebles')


# GESTIÓN DE ESTADOS DE MUEBLES
@login_required
@user_passes_test(lambda u: u.groups.filter(name__in=['admin', 'vendedores', 'finanzas']).exists(),login_url='IDindex')
def paginaGestionEstadosMuebles(request):
    estados_list = estadoMueble.objects.all()
    
    datos = {
        'estados': estados_list
    }
    
    return render(request, 'gestiones/administracion/administrador/gestionEstadosMuebles.html', datos)


@login_required
@user_passes_test(lambda u: u.groups.filter(name__in=['admin', 'vendedores', 'finanzas']).exists(),login_url='IDindex')
def paginaGestionCrearEstadoMueble(request):
    if request.method == 'POST':
        descripcion = request.POST.get('descripcion')
        if descripcion:
            nuevo_estado = estadoMueble(descripcion=descripcion)
            nuevo_estado.save()
            messages.success(request, 'Estado de mueble creado exitosamente.')
            return redirect('IDpaginaGestionEstadosMuebles')
        else:
            messages.error(request, 'Por favor, completa todos los campos.')
    
    return render(request, 'gestiones/administracion/administrador/gestionCrearEstadoMueble.html')


@login_required
@user_passes_test(lambda u: u.groups.filter(name__in=['admin', 'vendedores', 'finanzas']).exists(),login_url='IDindex')
def paginaGestionEditarEstadoMueble(request, id):
    try:
        estado_obj = estadoMueble.objects.get(id=id)
    except estadoMueble.DoesNotExist:
        messages.error(request, 'El estado no existe.')
        return redirect('IDpaginaGestionEstadosMuebles')
    
    if request.method == 'POST':
        descripcion = request.POST.get('descripcion')
        if descripcion:
            estado_obj.descripcion = descripcion
            estado_obj.save()
            messages.success(request, 'Estado actualizado exitosamente.')
            return redirect('IDpaginaGestionEstadosMuebles')
        else:
            messages.error(request, 'Por favor, completa todos los campos.')
    
    datos = {
        'estado': estado_obj
    }
    
    return render(request, 'gestiones/administracion/administrador/gestionEditarEstadoMueble.html', datos)


@login_required
@user_passes_test(lambda u: u.groups.filter(name__in=['admin', 'vendedores', 'finanzas']).exists(),login_url='IDindex')
def paginaGestionEliminarEstadoMueble(request, id):
    try:
        estado_obj = estadoMueble.objects.get(id=id)
        estado_obj.delete()
        messages.success(request, 'Estado eliminado exitosamente.')
    except estadoMueble.DoesNotExist:
        messages.error(request, 'El estado no existe.')
    
    return redirect('IDpaginaGestionEstadosMuebles')


# GESTIÓN DE ESTADOS DE PRODUCTOS COMPRADOS
@login_required
@user_passes_test(lambda u: u.groups.filter(name__in=['admin', 'vendedores', 'finanzas']).exists(),login_url='IDindex')
def paginaGestionEstadosProductosComprados(request):
    estados_list = estadoProductoComprado.objects.all()
    
    datos = {
        'estados': estados_list
    }
    
    return render(request, 'gestiones/administracion/administrador/gestionEstadosProductosComprados.html', datos)


@login_required
@user_passes_test(lambda u: u.groups.filter(name__in=['admin', 'vendedores', 'finanzas']).exists(),login_url='IDindex')
def paginaGestionCrearEstadoProductoComprado(request):
    if request.method == 'POST':
        descripcion = request.POST.get('descripcion')
        if descripcion:
            nuevo_estado = estadoProductoComprado(descripcion=descripcion)
            nuevo_estado.save()
            messages.success(request, 'Estado de producto comprado creado exitosamente.')
            return redirect('IDpaginaGestionEstadosProductosComprados')
        else:
            messages.error(request, 'Por favor, completa todos los campos.')
    
    return render(request, 'gestiones/administracion/administrador/gestionCrearEstadoProductoComprado.html')


@login_required
@user_passes_test(lambda u: u.groups.filter(name__in=['admin', 'vendedores', 'finanzas']).exists(),login_url='IDindex')
def paginaGestionEditarEstadoProductoComprado(request, id):
    try:
        estado_obj = estadoProductoComprado.objects.get(idestadocompra=id)
    except estadoProductoComprado.DoesNotExist:
        messages.error(request, 'El estado no existe.')
        return redirect('IDpaginaGestionEstadosProductosComprados')
    
    if request.method == 'POST':
        descripcion = request.POST.get('descripcion')
        if descripcion:
            estado_obj.descripcion = descripcion
            estado_obj.save()
            messages.success(request, 'Estado actualizado exitosamente.')
            return redirect('IDpaginaGestionEstadosProductosComprados')
        else:
            messages.error(request, 'Por favor, completa todos los campos.')
    
    datos = {
        'estado': estado_obj
    }
    
    return render(request, 'gestiones/administracion/administrador/gestionEditarEstadoProductoComprado.html', datos)


@login_required
@user_passes_test(lambda u: u.groups.filter(name__in=['admin', 'vendedores', 'finanzas']).exists(),login_url='IDindex')
def paginaGestionEliminarEstadoProductoComprado(request, id):
    try:
        estado_obj = estadoProductoComprado.objects.get(idestadocompra=id)
        estado_obj.delete()
        messages.success(request, 'Estado eliminado exitosamente.')
    except estadoProductoComprado.DoesNotExist:
        messages.error(request, 'El estado no existe.')
    
    return redirect('IDpaginaGestionEstadosProductosComprados')





@login_required
@user_passes_test(lambda u: u.groups.filter(name__in=['admin', 'vendedores', 'finanzas']).exists(),login_url='IDindex')




def paginaGestionEditarUsuario(request, id):
    usuario = User.objects.get(id=id)
    grupos = Group.objects.all()

    if request.method == 'POST':
        username = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        grupo_id = request.POST.get('grupo')

        usuario.username = username

        if password1:
            if password1 != password2:
                messages.error(request, 'Las contraseñas no coinciden.')
                return redirect('IDpaginaGestionEditarUsuario', id=id)

            usuario.set_password(password1)

        # Cambiar grupo
        if grupo_id:
            grupo = Group.objects.get(id=grupo_id)

            # Elimina grupos anteriores
            usuario.groups.clear()

            # Agrega el nuevo grupo
            usuario.groups.add(grupo)

        usuario.save()

        messages.success(request, 'Usuario actualizado correctamente.')
        return redirect('IDpaginaGestionUsuarios')

    return render(
        request,
        'gestiones/administracion/administrador/gestionEditarUsuario.html',
        {
            'usuario': usuario,
            'grupos': grupos
        }
    )





from django.template.loader import get_template
from xhtml2pdf import pisa

def reporteDeFinanzas(request):
    fecha_chile = timezone.now().astimezone( ZoneInfo("America/Santiago"))
    ventas = compra.objects.filter(
        fecha__year=fecha_chile.year,
        fecha__month=fecha_chile.month
    ).order_by('-fecha')
    detalleCompras = detalleCompra.objects.all()
    muebles = mueble.objects.all()
    total = sum(v.total for v in ventas)
    totalDecompras = 0
    totalDineroRecaudado = 0
    MueblesVendidos = {}

    for x in ventas:
        totalDecompras += 1
        totalDineroRecaudado += x.total

        for d in detalleCompras:
            if x.idCompra == d.idCompra.idCompra:

                nombre = d.idMueble.nombre

                if nombre not in MueblesVendidos:
                    MueblesVendidos[nombre] = 0

                MueblesVendidos[nombre] += d.cantidad
    # Cantidad máxima y mínima vendida
        max_cantidad = max(MueblesVendidos.values())
        min_cantidad = min(MueblesVendidos.values())

        # Todos los muebles con la cantidad máxima
        mas_vendidos = [
            (nombre, cantidad)
            for nombre, cantidad in MueblesVendidos.items()
            if cantidad == max_cantidad
        ]

        menos_vendidos = [
            (nombre, cantidad)
            for nombre, cantidad in MueblesVendidos.items()
            if cantidad == min_cantidad
        ]             
        datos = {
            'ventas': ventas, 
            'total': total,
            'detalleCompras': detalleCompras,
            'muebles': muebles,
            'fecha_chile':fecha_chile,
            'totalDecompras':totalDecompras,
            'totalDineroRecaudado':totalDineroRecaudado,
            'MueblesVendidos':MueblesVendidos,
            'masVendidos':mas_vendidos,
            'menosVendidos':menos_vendidos,
        }
    template = get_template('gestiones/reportesFinanzas.html')
    html = template.render(datos)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte_finanzas.pdf"'

    pisa.CreatePDF(html, dest=response)

    return response
from urllib import request
from django.shortcuts import render,redirect
from .forms import *
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User,Group
from django.core.paginator import Paginator
from django.contrib import messages

# Create your views here.
def index(request):
    return render(request,'menu.html')
# Create your views here.
def paginaProductos(request):
    return render(request,'productos.html')



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

    carrito_id = request.session.get(
        'carrito_id'
    )

    # carrito vacío
    if not carrito_id:

        return render(
            request,
            'carrito.html',
            {
                'detalles': [],
                'carrito': None
            }
        )

    carrito = compra.objects.get(
        idCompra=carrito_id
    )

    detalles = carrito.detalles.all()

    return render(
        request,
        'carrito.html',
        {
            'detalles': detalles,
            'carrito': carrito
        }
    )


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

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            return redirect('IDindex')


        else:
            return render(request, 'login.html', {
                'error': 'Usuario o contraseña incorrectos'
            })

    return render(request,'login/login.html')

def cerrarSesion(request):
    logout(request)
    return render(request,'menu.html')

# GESTION DE PERFIL DE USUARIO (CLIENTE)
def paginaPerfilCliente(request):
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

        # producto
        producto = mueble.objects.get(id=id)
        # cantidad
        cantidad = int(
            request.POST.get('cantidad')
        )

        # buscar carrito sesión
        carrito_id = request.session.get(
            'carrito_id'
        )

        # crear carrito si no existe
        if not carrito_id:

            cliente = cuenta.objects.get(
                usuario_cuenta=request.user.id
            )

            carrito = compra.objects.create(

                idCliente=cliente,

                total=0,

                completada=False
            )

            request.session['carrito_id'] = carrito.idCompra

        else:

            carrito = compra.objects.get(
                idCompra=carrito_id
            )

        # buscar item
        item, creado = detalleCompra.objects.get_or_create(

            idCompra=carrito,

            idMueble=producto,

            defaults={
                'cantidad': cantidad,
                'subtotal': producto.precio * cantidad
            }
        )

        # si ya existe sumar cantidad
        if not creado:

            item.cantidad += cantidad

            item.subtotal = (
                item.cantidad *
                producto.precio
            )

            item.save()

        # recalcular total
        total = 0

        for detalle in carrito.detalles.all():

            total += detalle.subtotal

        carrito.total = total
        carrito.save()
        messages.success(
            request,
            'Producto agregado al carrito correctamente'
        )
        return redirect('ver_carrito')
    return redirect('ver_carrito')
def eliminar_item_carrito(request, id):

    detalle = detalleCompra.objects.get(idDetalle=id)

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
        cliente = cuenta.objects.get(
            usuario_cuenta=request.user.id
        )

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
def historial_compras(request):
    compras = compra.objects.all()
    detalleCompras = detalleCompra.objects.all()
    datos = {
        'comprasCliente' : compras,
        'detallesComprasCliente' : detalleCompras,
    }
    return render(request,'pedido.html',datos)



# GESTIONES
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







def paginaGestionMuebles(request):
    muebles = mueble.objects.all()
    datos = {
        'muebles':muebles,
    }
    return render(request,'gestiones/administracion/vendedor/gestionMuebles.html',datos)

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

def paginaGestionPedidos(request):
    return render(request,'gestiones/administracion/gestionPedidos.html')

# GESTION DE COMPRAS
def paginaGestionCompras(request):
    comprasTotales = compra.objects.all()
    detalleComprasTotales = detalleCompra.objects.all()
    datos = {
        'compras':comprasTotales,
        'detalleCompras':detalleComprasTotales,
    }
    return render(request,'gestiones/administracion/gestionPedidos.html',datos)


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

def paginaGestionUsuarios(request):
    usuarios = User.objects.all()

    datos = {
        'usuarios': usuarios
    }

    return render(request, 'gestiones/administracion/administrador/gestionUsuarios.html', datos)



# GESTION CREAR CUENTA
def paginaGestionCrearCuenta(request):
    datos = {
        'formularioCuenta' : perfilClienteform(),
        'formularioUser' : UserCreationForm(),

    }

    return render(request, 'gestiones/administracion/administrador/gestionCrearCuenta.html',datos)

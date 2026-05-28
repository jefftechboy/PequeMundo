from django.urls import path
from .views import *

urlpatterns = [
    path('', index,name='IDindex'),
    path('paginaProductos/', listarCatalogo,name='IDpaginaProductos'),
    path('login/', paginaLogin,name='IDpaginalogin'),
    # PERFIL CLIENTE
    path('perfil/', paginaPerfilCliente,name='IDpaginaPerfilCliente'),
    path('editar_perfil/<int:id>/', actualizarPerfilCliente,name='IDactualizarPerfilCliente'),


    path('historial_compras/', historial_compras,name='IDhistorial_compras'),
    path('gestion-muebles/', gestion_muebles,name='gestion_muebles'),
    path('crearCuenta/', paginaCrearCuenta,name='IDpaginaCrearCuenta'),



    path('menu/', cerrarSesion,name='IDcerrarSesion'),


    #CARRITO
    # urls.py

    path('agregar-carrito/<int:id>/',agregar_carrito,name='agregar_carrito'),
    path('carrito/',paginaCarrito,name='ver_carrito'),
    path('finalizar-compra/',finalizar_compra,name='finalizar_compra'),
    path('eliminar-carrito/<int:id>/',eliminar_item_carrito,name='IDeliminarCarrito'
),

    # GESTIONES
    path('paginaInicioGestiones/', paginaInicioGestiones,name='IDpaginaInicioGestiones'),
    path('paginaGestionMuebles/', paginaGestionMuebles,name='IDpaginaGestionMuebles'),

    path('paginaEditarMueble/<int:id>/', modificar_mueble,name='IDpaginaEditarMuebles'),
    path('paginaCrearMueble', crearMueble,name='IDpaginaCrearMueble'),


    #Pagina gestionar compras

    path('paginaGestionCompras/', paginaGestionCompras,name='IDpaginaGestionCompras'),
    path('actualizarPedidos/<int:id>/', actualizarPedidos,name='IDpaginaActualizarCompras'),

    # PAGINA GESTION USUARIOS
    path('paginaGestionUsuarios/', paginaGestionUsuarios,name='IDpaginaGestionUsuarios'),
    path('paginaGestionCrearCuenta/', paginaGestionCrearCuenta,name='IDpaginaGestionCrearCuenta'),

]
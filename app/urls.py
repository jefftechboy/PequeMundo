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
   
    # PAGINA GESTION COMUNAS
    path('paginaGestionComunas/', paginaGestionComunas, name='IDpaginaGestionComunas'),
    path('paginaGestionCrearComuna/', paginaGestionCrearComuna, name='IDpaginaGestionCrearComuna'),
    path('paginaGestionEditarComuna/<int:id>/', paginaGestionEditarComuna, name='IDpaginaGestionEditarComuna'),
    path('paginaGestionEliminarComuna/<int:id>/', paginaGestionEliminarComuna, name='IDpaginaGestionEliminarComuna'),

    # PAGINA GESTION TIPOS DE ENVIO
    path('paginaGestionTiposEnvio/', paginaGestionTiposEnvio, name='IDpaginaGestionTiposEnvio'),
    path('paginaGestionCrearTipoEnvio/', paginaGestionCrearTipoEnvio, name='IDpaginaGestionCrearTipoEnvio'),
    path('paginaGestionEditarTipoEnvio/<int:id>/', paginaGestionEditarTipoEnvio, name='IDpaginaGestionEditarTipoEnvio'),

    # PAGINA GESTION TIPOS DE CUENTA
    path('paginaGestionTiposCuenta/', paginaGestionTiposCuenta, name='IDpaginaGestionTiposCuenta'),
    path('paginaGestionCrearTipoCuenta/', paginaGestionCrearTipoCuenta, name='IDpaginaGestionCrearTipoCuenta'),
    path('paginaGestionEditarTipoCuenta/<int:id>/', paginaGestionEditarTipoCuenta, name='IDpaginaGestionEditarTipoCuenta'),
    path('paginaGestionEliminarTipoCuenta/<int:id>/', paginaGestionEliminarTipoCuenta, name='IDpaginaGestionEliminarTipoCuenta'),

    # PAGINA GESTION PERFILES
    path('paginaGestionPerfiles/', paginaGestionPerfiles, name='IDpaginaGestionPerfiles'),
    path('paginaGestionCrearPerfil/', paginaGestionCrearPerfil, name='IDpaginaGestionCrearPerfil'),
    path('paginaGestionEditarPerfil/<int:id>/', paginaGestionEditarPerfil, name='IDpaginaGestionEditarPerfil'),
    path('paginaGestionEliminarPerfil/<int:id>/', paginaGestionEliminarPerfil, name='IDpaginaGestionEliminarPerfil'),

    # PAGINA GESTION DISPONIBILIDADES
    path('paginaGestionDisponibilidades/', paginaGestionDisponibilidades, name='IDpaginaGestionDisponibilidades'),
    path('paginaGestionCrearDisponibilidad/', paginaGestionCrearDisponibilidad, name='IDpaginaGestionCrearDisponibilidad'),
    path('paginaGestionEditarDisponibilidad/<int:id>/', paginaGestionEditarDisponibilidad, name='IDpaginaGestionEditarDisponibilidad'),
    path('paginaGestionEliminarDisponibilidad/<int:id>/', paginaGestionEliminarDisponibilidad, name='IDpaginaGestionEliminarDisponibilidad'),

    # PAGINA GESTION CATEGORIAS DE MUEBLES
    path('paginaGestionCategoriasMuebles/', paginaGestionCategoriasMuebles, name='IDpaginaGestionCategoriasMuebles'),
    path('paginaGestionCrearCategoriaMueble/', paginaGestionCrearCategoriaMueble, name='IDpaginaGestionCrearCategoriaMueble'),
    path('paginaGestionEditarCategoriaMueble/<int:id>/', paginaGestionEditarCategoriaMueble, name='IDpaginaGestionEditarCategoriaMueble'),
    path('paginaGestionEliminarCategoriaMueble/<int:id>/', paginaGestionEliminarCategoriaMueble, name='IDpaginaGestionEliminarCategoriaMueble'),

    # PAGINA GESTION ESTADOS DE MUEBLES
    path('paginaGestionEstadosMuebles/', paginaGestionEstadosMuebles, name='IDpaginaGestionEstadosMuebles'),
    path('paginaGestionCrearEstadoMueble/', paginaGestionCrearEstadoMueble, name='IDpaginaGestionCrearEstadoMueble'),
    path('paginaGestionEditarEstadoMueble/<int:id>/', paginaGestionEditarEstadoMueble, name='IDpaginaGestionEditarEstadoMueble'),
    path('paginaGestionEliminarEstadoMueble/<int:id>/', paginaGestionEliminarEstadoMueble, name='IDpaginaGestionEliminarEstadoMueble'),

    # PAGINA GESTION ESTADOS DE PRODUCTOS COMPRADOS
    path('paginaGestionEstadosProductosComprados/', paginaGestionEstadosProductosComprados, name='IDpaginaGestionEstadosProductosComprados'),
    path('paginaGestionCrearEstadoProductoComprado/', paginaGestionCrearEstadoProductoComprado, name='IDpaginaGestionCrearEstadoProductoComprado'),
    path('paginaGestionEditarEstadoProductoComprado/<int:id>/', paginaGestionEditarEstadoProductoComprado, name='IDpaginaGestionEditarEstadoProductoComprado'),
    path('paginaGestionEliminarEstadoProductoComprado/<int:id>/', paginaGestionEliminarEstadoProductoComprado, name='IDpaginaGestionEliminarEstadoProductoComprado'),

    # MERCADOPAGO
    path('pago/iniciar/', crear_preferencia_mp, name='crear_preferencia_mp'),
    path('pago/exitoso/', pago_exitoso, name='pago_exitoso'),
    path('pago/fallido/', pago_fallido, name='pago_fallido'),
    path('pago/pendiente/', pago_pendiente, name='pago_pendiente'),
    path('pago/webhook/', webhook_mp, name='webhook_mp'),
]
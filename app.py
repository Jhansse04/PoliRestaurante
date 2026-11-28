"""Punto de entrada de PoliRestaurante.

Ensambla las clases del diagrama (DAO -> Managers -> Controladores, Factory, Observer y Proxy),
registra las rutas HTTP que conectan las vistas con los controladores y arranca el servidor.
Aquí no hay lógica de negocio: solo el cableado entre las clases.

Ejecución:  python app.py
"""
import logging
from datetime import date, datetime
from decimal import Decimal

import pyodbc
from flask import Flask, jsonify, redirect, render_template, session
from flask_socketio import SocketIO, join_room
from werkzeug.exceptions import HTTPException

import config
from controladores import (RUTAS_POR_ROL, AdministradorController, PedidoController, ProductoController,
                           UsuarioController)
from dao import (AdministradorDAO, ClienteDAO, CocinaDAO, DetallePedidoDAO, MesaDAO, MeseroDAO, PedidoDAO,
                 ProductoDAO)
from dao.conexion import ConexionPorRol
from entidades import ROL_ADMINISTRADOR, ROL_CLIENTE, ROL_COCINA, ROL_MESERO
from entidades.pedido import TIPO_DOMICILIO, TIPO_MESA
from fabricas import PedidoDomicilioFactory, PedidoMesaFactory
from managers import AdministracionManager, PedidoManager, ProductoManager, UsuarioManager
from observadores import (AdministradorObserver, CanalTiempoReal, ClienteObserver, CocinaObserver,
                          MeseroObserver)
from proxy import AdministradorProxy, SesionUsuario

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

app = Flask(__name__, template_folder="vistas/templates", static_folder="vistas/static")
app.config.update(SECRET_KEY=config.SECRET_KEY, SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax")


def _serializar(objeto):
    """Cómo se escriben en JSON los tipos que usan las entidades."""
    if isinstance(objeto, Decimal):
        return float(objeto)
    if isinstance(objeto, (datetime, date)):
        return objeto.isoformat()
    raise TypeError("No se puede serializar %s" % type(objeto).__name__)


app.json.default = _serializar
app.json.sort_keys = False

# ====================================================================== ensamblaje
# DAO / persistencia (conexión dinámica según el rol de la sesión)
conexion = ConexionPorRol()
pedidoDAO = PedidoDAO(conexion)
detallePedidoDAO = DetallePedidoDAO(conexion)
mesaDAO = MesaDAO(conexion)
productoDAO = ProductoDAO(conexion)
administradorDAO = AdministradorDAO(conexion)
meseroDAO = MeseroDAO(conexion)
cocinaDAO = CocinaDAO(conexion)
clienteDAO = ClienteDAO(conexion)

# Managers / servicios
usuarioManager = UsuarioManager(administradorDAO, meseroDAO, cocinaDAO, clienteDAO)
productoManager = ProductoManager(productoDAO)
pedidoManager = PedidoManager(
    pedidoDAO, detallePedidoDAO, mesaDAO, productoManager, usuarioManager,
    {TIPO_MESA: PedidoMesaFactory(), TIPO_DOMICILIO: PedidoDomicilioFactory()},  # Factory
)
administracionManager = AdministracionManager(productoManager, usuarioManager, pedidoManager)

# Proxy / control de acceso
sesion = SesionUsuario()
administradorProxy = AdministradorProxy(administracionManager, sesion)

# Observer: PedidoManager publica y los cuatro observadores usan el canal en tiempo real
socketio = SocketIO(app, async_mode="threading")
canalTiempoReal = CanalTiempoReal(socketio)
for _observador in (CocinaObserver(canalTiempoReal), MeseroObserver(canalTiempoReal),
                    ClienteObserver(canalTiempoReal), AdministradorObserver(canalTiempoReal)):
    pedidoManager.suscribir(_observador)

# Controladores
usuarioController = UsuarioController(usuarioManager, sesion)
productoController = ProductoController(productoManager, sesion)
pedidoController = PedidoController(pedidoManager, sesion)
administradorController = AdministradorController(administradorProxy)  # recibe el Proxy como IAdminOperations

# ============================================================== rutas de la API (JSON)
_RUTAS_API = [
    # (ruta, métodos, método del controlador)
    ("/api/sesion", ["POST"], usuarioController.iniciarSesion),
    ("/api/sesion", ["DELETE"], usuarioController.cerrarSesion),
    ("/api/sesion", ["GET"], usuarioController.obtenerSesionActual),

    ("/api/menu", ["GET"], productoController.obtenerMenu),
    ("/api/menu/disponibles", ["GET"], productoController.listarProductosDisponibles),
    ("/api/productos/<int:idProducto>", ["GET"], productoController.consultarProducto),

    ("/api/pedidos", ["POST"], pedidoController.crearPedido),
    ("/api/pedidos", ["GET"], pedidoController.obtenerPedidos),
    ("/api/pedidos/historial", ["GET"], pedidoController.consultarHistorial),
    ("/api/pedidos/<int:idPedido>", ["GET"], pedidoController.obtenerPedido),
    ("/api/pedidos/<int:idPedido>/cancelar", ["POST"], pedidoController.cancelarPedido),
    ("/api/pedidos/<int:idPedido>/estado", ["PUT"], pedidoController.actualizarEstado),
    ("/api/pedidos/<int:idPedido>/entregar", ["POST"], pedidoController.marcarComoEntregado),

    ("/api/admin/productos", ["POST"], administradorController.crearProducto),
    ("/api/admin/productos/<int:idProducto>", ["PUT"], administradorController.modificarProducto),
    ("/api/admin/panel", ["GET"], administradorController.verPanelGeneral),
]
for _ruta, _metodos, _funcion in _RUTAS_API:
    app.add_url_rule(_ruta, endpoint="%s_%s" % (_funcion.__name__, _metodos[0]), view_func=_funcion,
                     methods=_metodos)


# ======================================================================= vistas (HTML)
def _servirVista(rol, plantilla):
    if not session.get("autenticado"):
        return redirect("/login")
    if session.get("rol") != rol:
        return redirect(RUTAS_POR_ROL.get(session.get("rol"), "/login"))
    return render_template(plantilla, nombre=session.get("nombre"))


@app.get("/")
def inicio():
    destino = RUTAS_POR_ROL.get(session.get("rol")) if session.get("autenticado") else None
    return redirect(destino or "/login")


@app.get("/login")
def login():
    destino = RUTAS_POR_ROL.get(session.get("rol")) if session.get("autenticado") else None
    return redirect(destino) if destino else render_template("login.html")


@app.get("/cliente")
def vistaCliente():
    return _servirVista(ROL_CLIENTE, "vista_cliente.html")


@app.get("/mesero")
def vistaMesero():
    return _servirVista(ROL_MESERO, "vista_mesero.html")


@app.get("/cocina")
def vistaCocina():
    return _servirVista(ROL_COCINA, "vista_cocina.html")


@app.get("/administrador")
def vistaAdministrador():
    return _servirVista(ROL_ADMINISTRADOR, "vista_administrador.html")


# ============================================= errores -> respuestas que piden las HU
def _respuestaError(error, estado):
    contenido = error.args[0] if error.args else None
    if isinstance(contenido, dict):  # {"error": ..., "campos": {...}}: indica qué datos fallaron
        return jsonify(contenido), estado
    return jsonify({"error": str(error)}), estado


@app.errorhandler(ValueError)
def _datosInvalidos(error):
    return _respuestaError(error, 400)


@app.errorhandler(LookupError)
def _noEncontrado(error):
    return _respuestaError(error, 404)


@app.errorhandler(PermissionError)
def _noAutorizado(error):
    return _respuestaError(error, 403 if session.get("autenticado") else 401)


@app.errorhandler(NotImplementedError)
def _noImplementado(error):
    return _respuestaError(error, 501)


@app.errorhandler(pyodbc.Error)
def _falloBaseDatos(error):
    app.logger.exception("Error de base de datos")
    return jsonify({"error": "No fue posible realizar su consulta, intente nuevamente"}), 503  # HU12 y HU13


@app.errorhandler(Exception)
def _errorInterno(error):
    if isinstance(error, HTTPException):
        return error
    app.logger.exception("Error interno")
    return jsonify({"error": "Ocurrió un error en el proceso. Intente nuevamente"}), 500  # HU13


# ======================================================= tiempo real (CanalTiempoReal)
@socketio.on("connect")
def _alConectar():
    """Suscribe la vista a la sala que le corresponde según su rol (sesión confiable)."""
    if not session.get("autenticado"):
        return False
    rol, idUsuario = session.get("rol"), session.get("idUsuario")
    if rol == ROL_COCINA:
        join_room("cocina")
    elif rol == ROL_MESERO:
        join_room("mesero")
    elif rol == ROL_ADMINISTRADOR:
        join_room("administrador")
    elif rol == ROL_CLIENTE:
        join_room("cliente:%s" % idUsuario)
    else:
        return False
    return True


if __name__ == "__main__":
    socketio.run(app, host=config.HOST, port=config.PUERTO, debug=config.DEBUG, allow_unsafe_werkzeug=True)

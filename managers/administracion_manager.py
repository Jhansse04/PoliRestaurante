"""AdministracionManager: RealSubject de IAdminOperations.

Coordina las operaciones administrativas delegando en ProductoManager, UsuarioManager y
PedidoManager. NO valida permisos: eso corresponde al AdministradorProxy.
"""
from proxy.i_admin_operations import IAdminOperations

_FUERA_DE_ALCANCE = "Funcionalidad fuera del alcance de las 15 historias de usuario"


class AdministracionManager(IAdminOperations):
    def __init__(self, productoManager, usuarioManager, pedidoManager):
        self._productoManager = productoManager
        self._usuarioManager = usuarioManager
        self._pedidoManager = pedidoManager

    # HU01
    def crearProducto(self, datos):
        return self._productoManager.crearProducto(datos)

    # HU02
    def modificarProducto(self, idProducto, datos):
        return self._productoManager.modificarProducto(idProducto, datos)

    def eliminarProducto(self, idProducto):
        return self._productoManager.eliminarProducto(idProducto)

    def crearUsuario(self, datos):
        return self._usuarioManager.crearUsuario(datos)

    def modificarUsuario(self, idUsuario, datos):
        return self._usuarioManager.modificarUsuario(idUsuario, datos)

    def eliminarUsuario(self, idUsuario):
        return self._usuarioManager.eliminarUsuario(idUsuario)

    def cambiarRol(self, idUsuario, rol):
        return self._usuarioManager.cambiarRol(idUsuario, rol)

    def gestionarPermisos(self, rol, permisos):
        return self._usuarioManager.gestionarPermisos(rol, permisos)

    def consultarReportes(self, filtros):
        raise NotImplementedError(_FUERA_DE_ALCANCE)

    # HU12
    def verPanelGeneral(self, filtros):
        return self._pedidoManager.obtenerPanelGlobal(filtros)

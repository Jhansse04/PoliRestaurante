"""AdministradorProxy: proxy de protección de IAdminOperations.

Verifica sesión, rol de administrador y el permiso específico de cada operación ANTES de
delegar en el servicio real. Si falla la autorización no invoca al servicio real.
"""
import logging

from entidades import ROL_ADMINISTRADOR
from proxy.i_admin_operations import IAdminOperations

_registro = logging.getLogger(__name__)

_DENEGADO = ("Acceso denegado: la operación requiere una sesión de administrador "
             "con el permiso correspondiente")

# Permiso que exige cada operación administrativa.
PERMISO_POR_OPERACION = {
    "crearProducto": "crearProducto",
    "modificarProducto": "modificarProducto",
    "eliminarProducto": "eliminarProducto",
    "crearUsuario": "gestionarUsuarios",
    "modificarUsuario": "gestionarUsuarios",
    "eliminarUsuario": "gestionarUsuarios",
    "cambiarRol": "cambiarRol",
    "gestionarPermisos": "gestionarPermisos",
    "consultarReportes": "consultarReportes",
    "verPanelGeneral": "verPanelPedidos",
}


class AdministradorProxy(IAdminOperations):
    def __init__(self, servicioReal, sesion):
        self._servicioReal = servicioReal
        self._sesion = sesion

    # ---- verificaciones (privadas) ----
    def _verificarSesion(self):
        return self._sesion.autenticado and self._sesion.idUsuario is not None

    def _verificarRolAdministrador(self):
        return self._sesion.rol == ROL_ADMINISTRADOR

    def _verificarPermiso(self, accion):
        return PERMISO_POR_OPERACION[accion] in self._sesion.permisos

    def _autorizar(self, accion):
        if not self._verificarSesion():
            motivo = "sesión no iniciada"
        elif not self._verificarRolAdministrador():
            motivo = "el rol %s no es administrador" % self._sesion.rol
        elif not self._verificarPermiso(accion):
            motivo = "falta el permiso '%s'" % PERMISO_POR_OPERACION[accion]
        else:
            return True
        _registro.warning("Operación administrativa '%s' denegada: %s", accion, motivo)
        return False

    # ---- operaciones: autorizar y luego delegar ----
    def crearProducto(self, datos):
        if not self._autorizar("crearProducto"):
            raise PermissionError(_DENEGADO)
        return self._servicioReal.crearProducto(datos)

    def modificarProducto(self, idProducto, datos):
        if not self._autorizar("modificarProducto"):
            raise PermissionError(_DENEGADO)
        return self._servicioReal.modificarProducto(idProducto, datos)

    def eliminarProducto(self, idProducto):
        if not self._autorizar("eliminarProducto"):
            raise PermissionError(_DENEGADO)
        return self._servicioReal.eliminarProducto(idProducto)

    def crearUsuario(self, datos):
        if not self._autorizar("crearUsuario"):
            raise PermissionError(_DENEGADO)
        return self._servicioReal.crearUsuario(datos)

    def modificarUsuario(self, idUsuario, datos):
        if not self._autorizar("modificarUsuario"):
            raise PermissionError(_DENEGADO)
        return self._servicioReal.modificarUsuario(idUsuario, datos)

    def eliminarUsuario(self, idUsuario):
        if not self._autorizar("eliminarUsuario"):
            raise PermissionError(_DENEGADO)
        return self._servicioReal.eliminarUsuario(idUsuario)

    def cambiarRol(self, idUsuario, rol):
        if not self._autorizar("cambiarRol"):
            raise PermissionError(_DENEGADO)
        return self._servicioReal.cambiarRol(idUsuario, rol)

    def gestionarPermisos(self, rol, permisos):
        if not self._autorizar("gestionarPermisos"):
            raise PermissionError(_DENEGADO)
        return self._servicioReal.gestionarPermisos(rol, permisos)

    def consultarReportes(self, filtros):
        if not self._autorizar("consultarReportes"):
            raise PermissionError(_DENEGADO)
        return self._servicioReal.consultarReportes(filtros)

    def verPanelGeneral(self, filtros):
        if not self._autorizar("verPanelGeneral"):
            raise PermissionError(_DENEGADO)
        return self._servicioReal.verPanelGeneral(filtros)

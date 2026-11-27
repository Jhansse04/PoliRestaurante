"""IAdminOperations (interfaz): contrato de las operaciones administrativas.

Lo implementan AdministracionManager (servicio real) y AdministradorProxy (control de acceso).
"""
from abc import ABC, abstractmethod


class IAdminOperations(ABC):
    @abstractmethod
    def crearProducto(self, datos): ...

    @abstractmethod
    def modificarProducto(self, idProducto, datos): ...

    @abstractmethod
    def eliminarProducto(self, idProducto): ...

    @abstractmethod
    def crearUsuario(self, datos): ...

    @abstractmethod
    def modificarUsuario(self, idUsuario, datos): ...

    @abstractmethod
    def eliminarUsuario(self, idUsuario): ...

    @abstractmethod
    def cambiarRol(self, idUsuario, rol): ...

    @abstractmethod
    def gestionarPermisos(self, rol, permisos): ...

    @abstractmethod
    def consultarReportes(self, filtros): ...

    @abstractmethod
    def verPanelGeneral(self, filtros): ...

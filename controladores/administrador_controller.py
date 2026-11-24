"""AdministradorController: operaciones administrativas.

Depende únicamente del contrato IAdminOperations; en tiempo de ejecución recibe el
AdministradorProxy, que verifica sesión, rol y permiso antes de delegar en el servicio real.
"""
from dataclasses import asdict

from flask import jsonify, request


class AdministradorController:
    def __init__(self, adminOperations):
        self._admin = adminOperations  # IAdminOperations (instancia concreta: AdministradorProxy)

    @staticmethod
    def _cuerpo():
        datos = request.get_json(silent=True)
        if datos is None:
            return {}
        if not isinstance(datos, dict):
            raise ValueError("El cuerpo de la solicitud debe ser un objeto JSON")
        return datos

    # HU01
    def crearProducto(self):
        producto = self._admin.crearProducto(self._cuerpo())
        return jsonify({"mensaje": "Producto creado correctamente", "producto": asdict(producto)}), 201

    # HU02
    def modificarProducto(self, idProducto):
        producto = self._admin.modificarProducto(idProducto, self._cuerpo())
        return jsonify({"mensaje": "Producto actualizado correctamente", "producto": asdict(producto)})

    # HU12
    def verPanelGeneral(self):
        pedidos = self._admin.verPanelGeneral(request.args.to_dict())
        return jsonify({"pedidos": pedidos, "mensaje": None if pedidos else "No hay pedidos para mostrar"})

    # ---- Operaciones del diagrama que ninguna de las 15 HU requiere ----
    def eliminarProducto(self, idProducto):
        return jsonify(self._admin.eliminarProducto(idProducto))

    def crearUsuario(self):
        return jsonify(self._admin.crearUsuario(self._cuerpo()))

    def modificarUsuario(self, idUsuario):
        return jsonify(self._admin.modificarUsuario(idUsuario, self._cuerpo()))

    def eliminarUsuario(self, idUsuario):
        return jsonify(self._admin.eliminarUsuario(idUsuario))

    def cambiarRol(self, idUsuario):
        return jsonify(self._admin.cambiarRol(idUsuario, self._cuerpo().get("rol")))

    def gestionarPermisos(self):
        cuerpo = self._cuerpo()
        return jsonify(self._admin.gestionarPermisos(cuerpo.get("rol"), cuerpo.get("permisos")))

    def consultarReportes(self):
        return jsonify(self._admin.consultarReportes(request.args.to_dict()))

"""ProductoController: consulta del menú (solo lectura). HU14."""
from dataclasses import asdict

from flask import jsonify


class ProductoController:
    def __init__(self, productoManager, sesion):
        self._productoManager = productoManager
        self._sesion = sesion

    def _exigirSesion(self):
        if not self._sesion.autenticado:
            raise PermissionError("Debe iniciar sesión para consultar el menú")

    def obtenerMenu(self):
        """Todos los productos; los no disponibles se muestran con disponible=false (HU14 esc. 4)."""
        self._exigirSesion()
        productos = self._productoManager.listarProductos()
        return jsonify({"productos": [asdict(p) for p in productos]})

    def consultarProducto(self, idProducto):
        """Vista ampliada de un producto: nombre, precio, imagen, descripción e ingredientes (HU14 esc. 2)."""
        self._exigirSesion()
        return jsonify(asdict(self._productoManager.consultarProducto(idProducto)))

    def listarProductosDisponibles(self):
        self._exigirSesion()
        productos = self._productoManager.listarProductos(soloDisponibles=True)
        return jsonify({"productos": [asdict(p) for p in productos]})

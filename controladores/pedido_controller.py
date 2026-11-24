"""PedidoController: operaciones de pedidos "por rol" (mesero, cocina y cliente)."""
from flask import jsonify, request


class PedidoController:
    def __init__(self, pedidoManager, sesion):
        self._pedidoManager = pedidoManager
        self._sesion = sesion

    def _actor(self):
        """(rol, idUsuario) de la sesión confiable; nunca se toman del cuerpo de la solicitud."""
        if not self._sesion.autenticado:
            raise PermissionError("Debe iniciar sesión para realizar esta operación")
        return self._sesion.rol, self._sesion.idUsuario

    @staticmethod
    def _cuerpo():
        datos = request.get_json(silent=True)
        if datos is None:
            return {}
        if not isinstance(datos, dict):
            raise ValueError("El cuerpo de la solicitud debe ser un objeto JSON")
        return datos

    # HU03 (mesero, mesa) y HU10 (cliente, domicilio)
    def crearPedido(self):
        rol, idUsuario = self._actor()
        return jsonify(self._pedidoManager.crearPedido(self._cuerpo(), rol, idUsuario)), 201

    # HU04, HU09, HU11, HU13
    def obtenerPedido(self, idPedido):
        rol, idUsuario = self._actor()
        return jsonify(self._pedidoManager.obtenerPedido(idPedido, rol, idUsuario))

    # HU07 (cocina), HU13 (mesero), HU11 (cliente)
    def obtenerPedidos(self):
        rol, idUsuario = self._actor()
        pedidos = self._pedidoManager.obtenerPedidos(rol, idUsuario)
        return jsonify({"pedidos": pedidos, "mensaje": None if pedidos else "No hay pedidos para mostrar"})

    # HU05 (mesero) y HU15 (cliente, con confirmación)
    def cancelarPedido(self, idPedido):
        rol, idUsuario = self._actor()
        confirmar = self._cuerpo().get("confirmar") is True
        return jsonify(self._pedidoManager.cancelarPedido(idPedido, rol, idUsuario, confirmar))

    # HU08 (cocina) y HU13 (mesero)
    def actualizarEstado(self, idPedido):
        rol, idUsuario = self._actor()
        estado = self._cuerpo().get("estado")
        return jsonify(self._pedidoManager.actualizarEstado(idPedido, estado, rol, idUsuario))

    # HU13
    def marcarComoEntregado(self, idPedido):
        rol, idUsuario = self._actor()
        return jsonify(self._pedidoManager.marcarComoEntregado(idPedido, rol, idUsuario))

    # HU06 (mesero) y HU11 (cliente)
    def consultarHistorial(self):
        rol, idUsuario = self._actor()
        pedidos = self._pedidoManager.consultarHistorial(rol, idUsuario)
        mensaje = None
        if not pedidos:
            mensaje = ("Aún no has creado ningún pedido" if rol == "MESERO"
                       else "Aún no has realizado ningún pedido")
        return jsonify({"pedidos": pedidos, "mensaje": mensaje})

    # ---- Operaciones del diagrama que ninguna de las 15 HU requiere ----
    def marcarComoPagado(self, idPedido):
        rol, idUsuario = self._actor()
        return jsonify(self._pedidoManager.marcarComoPagado(idPedido, rol, idUsuario))

    def consultarPedidosPorMesa(self, idMesa):
        rol, idUsuario = self._actor()
        return jsonify(self._pedidoManager.consultarPedidosPorMesa(idMesa, rol, idUsuario))

    def consultarPedidosPorFecha(self):
        rol, idUsuario = self._actor()
        return jsonify(self._pedidoManager.consultarPedidosPorFecha(
            request.args.get("desde"), request.args.get("hasta"), rol, idUsuario))

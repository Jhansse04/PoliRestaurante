"""MeseroObserver: los meseros ven todos los pedidos (HU13), así que reciben sus novedades."""
from dataclasses import asdict

from observadores.pedido_observer import (EVENTO_ESTADO_CAMBIADO, EVENTO_PEDIDO_CANCELADO,
                                          EVENTO_PEDIDO_CREADO, PedidoObserver)


class MeseroObserver(PedidoObserver):
    _EVENTOS_RELEVANTES = (EVENTO_PEDIDO_CREADO, EVENTO_ESTADO_CAMBIADO, EVENTO_PEDIDO_CANCELADO)

    def __init__(self, canal):
        self._canal = canal

    def actualizar(self, pedido, evento):
        if evento not in self._EVENTOS_RELEVANTES:
            return
        self._canal.enviar("mesero", {"evento": evento, "pedido": asdict(pedido)})

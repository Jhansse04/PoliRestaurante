"""CocinaObserver: la cocina recibe pedidos nuevos, cambios de estado y cancelaciones."""
from dataclasses import asdict

from observadores.pedido_observer import (EVENTO_ESTADO_CAMBIADO, EVENTO_PEDIDO_CANCELADO,
                                          EVENTO_PEDIDO_CREADO, PedidoObserver)


class CocinaObserver(PedidoObserver):
    _EVENTOS_RELEVANTES = (EVENTO_PEDIDO_CREADO, EVENTO_ESTADO_CAMBIADO, EVENTO_PEDIDO_CANCELADO)

    def __init__(self, canal):
        self._canal = canal

    def actualizar(self, pedido, evento):
        if evento not in self._EVENTOS_RELEVANTES:
            return
        self._canal.enviar("cocina", {"evento": evento, "pedido": asdict(pedido)})

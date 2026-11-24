"""ClienteObserver: el cliente solo recibe los eventos de SUS propios pedidos."""
from dataclasses import asdict

from observadores.pedido_observer import EVENTOS, PedidoObserver


class ClienteObserver(PedidoObserver):
    def __init__(self, canal):
        self._canal = canal

    def actualizar(self, pedido, evento):
        if evento not in EVENTOS or pedido.id_cliente is None:
            return
        self._canal.enviar("cliente:%s" % pedido.id_cliente, {"evento": evento, "pedido": asdict(pedido)})

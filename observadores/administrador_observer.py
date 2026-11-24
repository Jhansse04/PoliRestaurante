"""AdministradorObserver: el administrador supervisa todos los eventos (panel general, HU12)."""
from dataclasses import asdict

from observadores.pedido_observer import EVENTOS, PedidoObserver


class AdministradorObserver(PedidoObserver):
    def __init__(self, canal):
        self._canal = canal

    def actualizar(self, pedido, evento):
        if evento not in EVENTOS:
            return
        self._canal.enviar("administrador", {"evento": evento, "pedido": asdict(pedido)})

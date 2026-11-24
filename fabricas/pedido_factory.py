"""PedidoFactory (interfaz): declara crearPedido(datos): Pedido."""
from abc import ABC, abstractmethod


class PedidoFactory(ABC):
    @abstractmethod
    def crearPedido(self, datos):
        """Valida los datos propios de la modalidad y construye el Pedido (sin persistirlo)."""

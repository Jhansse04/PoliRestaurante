"""PedidoObserver (interfaz): declara actualizar(pedido, evento) + vocabulario de eventos."""
from abc import ABC, abstractmethod

EVENTO_PEDIDO_CREADO = "PedidoCreado"
EVENTO_ESTADO_CAMBIADO = "EstadoPedidoCambiado"
EVENTO_PEDIDO_CANCELADO = "PedidoCancelado"
EVENTO_PAGO_ACTUALIZADO = "PagoActualizado"
EVENTOS = (EVENTO_PEDIDO_CREADO, EVENTO_ESTADO_CAMBIADO, EVENTO_PEDIDO_CANCELADO, EVENTO_PAGO_ACTUALIZADO)


class PedidoObserver(ABC):
    @abstractmethod
    def actualizar(self, pedido, evento):
        """Reacciona a un evento del ciclo de vida de un pedido."""

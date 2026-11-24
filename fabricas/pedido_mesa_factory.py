"""PedidoMesaFactory: pedido para consumo en mesa (requiere mesa y mesero; sin dirección)."""
from datetime import datetime
from decimal import Decimal

from entidades.pedido import ESTADO_PENDIENTE, TIPO_MESA, Pedido
from fabricas.pedido_factory import PedidoFactory


class PedidoMesaFactory(PedidoFactory):
    def crearPedido(self, datos):
        errores = {}
        mesa = datos.get("mesa")
        if mesa is None:
            errores["id_mesa"] = "La mesa indicada no existe o no fue informada"
        if datos.get("id_mesero") is None:
            errores["id_mesero"] = "El pedido de mesa requiere un mesero asignado"
        if datos.get("id_cliente") is None:
            errores["id_cliente"] = "El pedido requiere un cliente"
        if datos.get("id_cocina") is None:
            errores["id_cocina"] = "El pedido requiere una cocina asignada"
        if errores:
            raise ValueError({"error": "Datos del pedido de mesa inválidos", "campos": errores})

        ahora = datetime.now().replace(microsecond=0)  # DATETIME de SQL Server: precisión de segundos
        return Pedido(
            id_pedido=None,
            id_mesero=datos["id_mesero"],
            id_cocina=datos["id_cocina"],
            id_cliente=datos["id_cliente"],
            id_mesa=mesa.id_mesa,
            fecha=ahora,
            fecha_estado=ahora,
            tipo_pedido=TIPO_MESA,
            direccion=None,
            estado=ESTADO_PENDIENTE,
            pagado=False,
            medio_pago=None,
            total=datos.get("total", Decimal("0.00")),
        )

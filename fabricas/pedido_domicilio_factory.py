"""PedidoDomicilioFactory: pedido a domicilio (requiere dirección; sin mesa ni mesero)."""
from datetime import datetime
from decimal import Decimal

from entidades.pedido import ESTADO_PENDIENTE, TIPO_DOMICILIO, Pedido
from fabricas.pedido_factory import PedidoFactory


class PedidoDomicilioFactory(PedidoFactory):
    def crearPedido(self, datos):
        errores = {}
        direccion = datos.get("direccion")
        direccion = direccion.strip() if isinstance(direccion, str) else ""
        if not direccion or len(direccion) > 255:
            errores["direccion"] = "La dirección de entrega es obligatoria (máximo 255 caracteres)"
        if datos.get("id_cliente") is None:
            errores["id_cliente"] = "El pedido requiere un cliente"
        if datos.get("id_cocina") is None:
            errores["id_cocina"] = "El pedido requiere una cocina asignada"
        if errores:
            raise ValueError({"error": "Datos del pedido a domicilio inválidos", "campos": errores})

        ahora = datetime.now().replace(microsecond=0)  # DATETIME de SQL Server: precisión de segundos
        # HU10: un domicilio nunca tiene mesa ni mesero, aunque los datos los incluyan.
        return Pedido(
            id_pedido=None,
            id_mesero=None,
            id_cocina=datos["id_cocina"],
            id_cliente=datos["id_cliente"],
            id_mesa=None,
            fecha=ahora,
            fecha_estado=ahora,
            tipo_pedido=TIPO_DOMICILIO,
            direccion=direccion,
            estado=ESTADO_PENDIENTE,
            pagado=False,
            medio_pago=None,
            total=datos.get("total", Decimal("0.00")),
        )

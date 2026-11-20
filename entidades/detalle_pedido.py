"""Entidad DetallePedido (modelo). Tabla: DetallePedido (PK compuesta id_pedido + id_producto)."""
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional


@dataclass
class DetallePedido:
    id_pedido: Optional[int] = None
    id_producto: Optional[int] = None
    cantidad: int = 1
    precio_unitario: Decimal = Decimal("0.00")

"""Entidad Pedido (modelo). Tabla: Pedido."""
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional

ESTADO_PENDIENTE = "PENDIENTE"
ESTADO_EN_PREPARACION = "EN PREPARACION"
ESTADO_LISTO = "LISTO"
ESTADO_ENTREGADO = "ENTREGADO"
ESTADO_CANCELADO = "CANCELADO"
ESTADOS = (ESTADO_PENDIENTE, ESTADO_EN_PREPARACION, ESTADO_LISTO, ESTADO_ENTREGADO, ESTADO_CANCELADO)

TIPO_MESA = "MESA"
TIPO_DOMICILIO = "DOMICILIO"
TIPOS = (TIPO_MESA, TIPO_DOMICILIO)


@dataclass
class Pedido:
    id_pedido: Optional[int] = None
    id_mesero: Optional[int] = None
    id_cocina: Optional[int] = None
    id_cliente: Optional[int] = None
    id_mesa: Optional[int] = None
    fecha: Optional[datetime] = None
    fecha_estado: Optional[datetime] = None  # último cambio de estado (HU11 y HU12)
    tipo_pedido: str = TIPO_MESA
    direccion: Optional[str] = None
    estado: str = ESTADO_PENDIENTE
    pagado: bool = False
    medio_pago: Optional[str] = None
    total: Decimal = Decimal("0.00")

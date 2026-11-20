"""Entidad Producto (modelo). Tabla: Producto."""
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

TIPO_PLATO = "PLATO"
TIPO_BEBIDA = "BEBIDA"
TIPOS = (TIPO_PLATO, TIPO_BEBIDA)


@dataclass
class Producto:
    id_producto: Optional[int] = None
    nombre: str = ""
    descripcion: Optional[str] = None
    precio: Decimal = Decimal("0.00")
    tipo: str = TIPO_PLATO
    imagen: Optional[str] = None
    disponible: bool = True

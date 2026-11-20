"""Entidad Mesa (modelo). Tabla: Mesa."""
from dataclasses import dataclass
from typing import Optional

ESTADO_LIBRE = "LIBRE"
ESTADO_OCUPADA = "OCUPADA"
ESTADOS = (ESTADO_LIBRE, ESTADO_OCUPADA)


@dataclass
class Mesa:
    id_mesa: Optional[int] = None
    numero: Optional[int] = None
    capacidad: Optional[int] = None
    estado: str = ESTADO_LIBRE

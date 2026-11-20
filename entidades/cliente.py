"""Entidad Cliente (modelo). Tabla: Cliente."""
from dataclasses import dataclass
from typing import Optional

ROL = "CLIENTE"


@dataclass
class Cliente:
    id_usuario: Optional[int] = None
    nombre: str = ""
    correo: str = ""
    contrasena: str = ""  # hash, nunca texto plano
    telefono: Optional[str] = None
    rol: str = ROL

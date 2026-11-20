"""Entidad Cocina (modelo). Tabla: Cocina."""
from dataclasses import dataclass
from typing import Optional

ROL = "COCINA"


@dataclass
class Cocina:
    id_usuario: Optional[int] = None
    nombre: str = ""
    correo: str = ""
    contrasena: str = ""  # hash, nunca texto plano
    telefono: Optional[str] = None
    rol: str = ROL

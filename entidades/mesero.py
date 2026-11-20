"""Entidad Mesero (modelo). Tabla: Mesero."""
from dataclasses import dataclass
from typing import Optional

ROL = "MESERO"


@dataclass
class Mesero:
    id_usuario: Optional[int] = None
    nombre: str = ""
    correo: str = ""
    contrasena: str = ""  # hash, nunca texto plano
    telefono: Optional[str] = None
    rol: str = ROL

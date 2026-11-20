"""Entidad Administrador (modelo). Tabla: Administrador."""
from dataclasses import dataclass
from typing import Optional

ROL = "ADMINISTRADOR"


@dataclass
class Administrador:
    id_usuario: Optional[int] = None
    nombre: str = ""
    correo: str = ""
    contrasena: str = ""  # hash, nunca texto plano
    telefono: Optional[str] = None
    rol: str = ROL

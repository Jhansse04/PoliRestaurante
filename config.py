"""Configuración de PoliRestaurante.

Lee variables de entorno (o el archivo .env). Es solo configuración: no
contiene lógica de negocio ni forma parte de la arquitectura por capas.

Conexión a la base de datos:
  Se construye una cadena de conexión distinta por cada rol de la aplicación
  (ADMINISTRADOR, MESERO, COCINA, CLIENTE). Además se genera una cadena
  especial "AUTENTICACION" (solo lectura sobre las tablas de usuarios) que
  se usa antes de conocer el rol del usuario (es decir, durante el login).
"""
import os
import secrets

from dotenv import load_dotenv

load_dotenv()

DB_DRIVER = os.getenv("DB_DRIVER", "ODBC Driver 18 for SQL Server").strip()
DB_SERVIDOR = os.getenv("DB_SERVIDOR", "localhost").replace("/", "\\").strip()
DB_NOMBRE = os.getenv("DB_NOMBRE", "PoliRestaurante").strip()

# Credenciales por rol (SQL Server Authentication).
DB_USR_AUTENTICACION = os.getenv("DB_USR_AUTENTICACION", "login_autenticacion")
DB_PWD_AUTENTICACION = os.getenv("DB_PWD_AUTENTICACION", "")
DB_USR_ADMINISTRADOR = os.getenv("DB_USR_ADMINISTRADOR", "login_administrador")
DB_PWD_ADMINISTRADOR = os.getenv("DB_PWD_ADMINISTRADOR", "")
DB_USR_MESERO = os.getenv("DB_USR_MESERO", "login_mesero")
DB_PWD_MESERO = os.getenv("DB_PWD_MESERO", "")
DB_USR_COCINA = os.getenv("DB_USR_COCINA", "login_cocina")
DB_PWD_COCINA = os.getenv("DB_PWD_COCINA", "")
DB_USR_CLIENTE = os.getenv("DB_USR_CLIENTE", "login_cliente")
DB_PWD_CLIENTE = os.getenv("DB_PWD_CLIENTE", "")


def _construir_cadena(usuario, contrasena):
    """Construye una cadena de conexión ODBC para SQL Server."""
    partes = [
        "DRIVER={%s}" % DB_DRIVER,
        "SERVER=%s" % DB_SERVIDOR,
        "DATABASE=%s" % DB_NOMBRE,
        "TrustServerCertificate=yes",
    ]
    if usuario:
        partes.append("UID=%s" % usuario)
        partes.append("PWD={%s}" % contrasena.replace("}", "}}"))
    else:
        partes.append("Trusted_Connection=yes")
    return ";".join(partes)


# Cadena de conexión por rol: se selecciona dinámicamente según la sesión.
CADENAS_POR_ROL = {
    "AUTENTICACION": _construir_cadena(DB_USR_AUTENTICACION, DB_PWD_AUTENTICACION),
    "ADMINISTRADOR": _construir_cadena(DB_USR_ADMINISTRADOR, DB_PWD_ADMINISTRADOR),
    "MESERO":        _construir_cadena(DB_USR_MESERO, DB_PWD_MESERO),
    "COCINA":        _construir_cadena(DB_USR_COCINA, DB_PWD_COCINA),
    "CLIENTE":       _construir_cadena(DB_USR_CLIENTE, DB_PWD_CLIENTE),
}

# Cadena de solo lectura para autenticación (antes de conocer el rol).
CADENA_CONEXION = CADENAS_POR_ROL["AUTENTICACION"]

# Si no se define SECRET_KEY se genera una al arrancar (las sesiones se pierden al reiniciar).
SECRET_KEY = os.getenv("SECRET_KEY") or secrets.token_hex(32)
HOST = os.getenv("HOST", "127.0.0.1")
PUERTO = int(os.getenv("PUERTO", "5000"))
DEBUG = os.getenv("DEBUG", "false").strip().lower() in ("1", "true", "si", "sí")

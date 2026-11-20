"""Resolución dinámica de la cadena de conexión según el rol de la sesión Flask.

Antes de iniciar sesión (autenticación), se usa la cadena de login_autenticacion
que solo tiene SELECT sobre las tablas de usuarios.
Después de iniciar sesión, se usa la cadena correspondiente al rol del usuario
(ADMINISTRADOR, MESERO, COCINA o CLIENTE), cada una con sus GRANT y DENY propios.
"""
import logging

from flask import has_request_context, session

import config

_registro = logging.getLogger(__name__)


class ConexionPorRol:
    """Provee la cadena de conexión correcta según el rol almacenado en la sesión.

    Todos los DAOs comparten la misma instancia. Como no tiene estado mutable
    propio (lee de ``flask.session`` en cada llamada), es segura para uso
    concurrente entre solicitudes.
    """

    def obtener(self):
        """Devuelve la cadena de conexión que corresponde al rol de la sesión actual."""
        if has_request_context():
            rol = session.get("rol")
            if rol and rol in config.CADENAS_POR_ROL:
                _registro.debug("Conexión con rol: %s", rol)
                return config.CADENAS_POR_ROL[rol]
        # Sin sesión o sin rol → conexión de solo lectura (autenticación).
        return config.CADENAS_POR_ROL["AUTENTICACION"]

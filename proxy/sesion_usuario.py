"""SesionUsuario: contexto de sesión confiable (idUsuario, rol, permisos, autenticado).

Los valores se leen de la sesión firmada de Flask de la solicitud en curso, por lo que una
única instancia compartida es segura entre solicitudes concurrentes y el cliente no puede
alterarlos (la cookie va firmada con SECRET_KEY). Solo se escriben al iniciar sesión
(UsuarioController.iniciarSesion).
"""
from flask import session


class SesionUsuario:
    @property
    def idUsuario(self):
        return session.get("idUsuario")

    @property
    def rol(self):
        return session.get("rol")

    @property
    def permisos(self):
        return set(session.get("permisos", []))

    @property
    def autenticado(self):
        return bool(session.get("autenticado", False))

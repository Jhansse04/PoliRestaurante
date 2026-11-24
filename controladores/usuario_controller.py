"""UsuarioController: inicio y cierre de sesión (autenticación / sesión)."""
from flask import jsonify, request, session

from entidades import ROL_ADMINISTRADOR, ROL_CLIENTE, ROL_COCINA, ROL_MESERO

# Página de inicio de cada rol (la vista correspondiente del diagrama).
RUTAS_POR_ROL = {
    ROL_CLIENTE: "/cliente",
    ROL_MESERO: "/mesero",
    ROL_COCINA: "/cocina",
    ROL_ADMINISTRADOR: "/administrador",
}


class UsuarioController:
    def __init__(self, usuarioManager, sesion):
        self._usuarioManager = usuarioManager
        self._sesion = sesion

    def iniciarSesion(self):
        datos = request.get_json(silent=True)
        if not isinstance(datos, dict):
            raise ValueError("Los datos de inicio de sesión deben enviarse como un objeto JSON")
        datosSesion = self._usuarioManager.autenticar(datos.get("correo"), datos.get("contrasena"))

        session.clear()  # evita reutilizar una sesión anterior (fijación de sesión)
        session["autenticado"] = True
        session["idUsuario"] = datosSesion["idUsuario"]
        session["rol"] = datosSesion["rol"]
        session["permisos"] = datosSesion["permisos"]
        session["nombre"] = datosSesion["nombre"]
        return jsonify({
            "mensaje": "Bienvenido, %s" % datosSesion["nombre"],  # HU14 escenario 1
            "rol": datosSesion["rol"],
            "nombre": datosSesion["nombre"],
            "redireccion": RUTAS_POR_ROL[datosSesion["rol"]],
        })

    def cerrarSesion(self):
        session.clear()
        return jsonify({"mensaje": "Sesión cerrada correctamente"})

    def obtenerSesionActual(self):
        return jsonify({
            "autenticado": self._sesion.autenticado,
            "idUsuario": self._sesion.idUsuario,
            "rol": self._sesion.rol,
            "permisos": sorted(self._sesion.permisos),
            "nombre": session.get("nombre"),
        })

"""UsuarioManager: autenticación y consulta de usuarios (Administrador, Mesero, Cocina, Cliente)."""
from werkzeug.security import check_password_hash

from entidades import ROL_ADMINISTRADOR, ROL_CLIENTE, ROL_COCINA, ROL_MESERO, ROLES

_FUERA_DE_ALCANCE = "Funcionalidad fuera del alcance de las 15 historias de usuario"

# Permisos de cada rol (los consulta el AdministradorProxy a través de SesionUsuario).
PERMISOS_POR_ROL = {
    ROL_ADMINISTRADOR: {"crearProducto", "modificarProducto", "eliminarProducto", "gestionarUsuarios",
                        "cambiarRol", "gestionarPermisos", "consultarReportes", "verPanelPedidos"},
    ROL_MESERO: set(),
    ROL_COCINA: set(),
    ROL_CLIENTE: set(),
}


class UsuarioManager:
    def __init__(self, administradorDAO, meseroDAO, cocinaDAO, clienteDAO):
        self._daos = {
            ROL_ADMINISTRADOR: administradorDAO,
            ROL_MESERO: meseroDAO,
            ROL_COCINA: cocinaDAO,
            ROL_CLIENTE: clienteDAO,
        }

    def _dao(self, rol):
        if rol not in self._daos:
            raise ValueError("Rol inválido: %s" % rol)
        return self._daos[rol]

    def autenticar(self, correo, contrasena):
        """Valida las credenciales y devuelve los datos de la sesión (idUsuario, rol, nombre, permisos)."""
        errores = {}
        if not isinstance(correo, str) or not correo.strip():
            errores["correo"] = "Es obligatorio"
        if not isinstance(contrasena, str) or not contrasena:
            errores["contrasena"] = "Es obligatoria"
        if errores:
            raise ValueError({"error": "Datos de inicio de sesión inválidos", "campos": errores})

        correo = correo.strip().lower()
        # Los DAO de usuario no definen buscarPorCorreo, por eso se filtra sobre listar().
        for rol in ROLES:
            for usuario in self._daos[rol].listar():
                if usuario.correo.strip().lower() == correo and check_password_hash(usuario.contrasena, contrasena):
                    return {"idUsuario": usuario.id_usuario, "rol": rol, "nombre": usuario.nombre,
                            "permisos": sorted(PERMISOS_POR_ROL[rol])}
        raise PermissionError("Correo o contraseña incorrectos")

    def obtenerUsuario(self, idUsuario, rol):
        usuario = self._dao(rol).buscarPorId(idUsuario)
        if usuario is None:
            raise LookupError("El usuario no existe")
        return usuario

    def listarUsuarios(self, rol):
        return self._dao(rol).listar()

    # ---- Operaciones del diagrama que ninguna de las 15 HU requiere ----
    def crearUsuario(self, datos):
        raise NotImplementedError(_FUERA_DE_ALCANCE)

    def modificarUsuario(self, idUsuario, datos):
        raise NotImplementedError(_FUERA_DE_ALCANCE)

    def eliminarUsuario(self, idUsuario):
        raise NotImplementedError(_FUERA_DE_ALCANCE)

    def cambiarRol(self, idUsuario, rol):
        raise NotImplementedError(_FUERA_DE_ALCANCE)

    def gestionarPermisos(self, rol, permisos):
        raise NotImplementedError(_FUERA_DE_ALCANCE)

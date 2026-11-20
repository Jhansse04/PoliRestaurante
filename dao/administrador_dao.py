"""DAO de Administrador: único objeto que accede a la tabla Administrador."""
from contextlib import closing

import pyodbc

from entidades.administrador import Administrador

_COLUMNAS = "id_usuario, nombre, correo, contrasena, telefono, rol"


class AdministradorDAO:
    def __init__(self, conexion):
        self._conexion = conexion

    def _conectar(self):
        return pyodbc.connect(self._conexion.obtener())

    def guardar(self, administrador):
        sql = ("INSERT INTO Administrador (nombre, correo, contrasena, telefono, rol) "
               "OUTPUT INSERTED.id_usuario VALUES (?, ?, ?, ?, ?)")
        with closing(self._conectar()) as conexion:
            cursor = conexion.cursor()
            cursor.execute(sql, administrador.nombre, administrador.correo, administrador.contrasena, administrador.telefono, administrador.rol)
            administrador.id_usuario = int(cursor.fetchone()[0])
            conexion.commit()
        return administrador.id_usuario

    def buscarPorId(self, idUsuario):
        sql = "SELECT " + _COLUMNAS + " FROM Administrador WHERE id_usuario = ?"
        with closing(self._conectar()) as conexion:
            fila = conexion.cursor().execute(sql, idUsuario).fetchone()
        return Administrador(*fila) if fila else None

    def actualizar(self, administrador):
        sql = "UPDATE Administrador SET nombre = ?, correo = ?, contrasena = ?, telefono = ? WHERE id_usuario = ?"
        with closing(self._conectar()) as conexion:
            cursor = conexion.cursor()
            cursor.execute(sql, administrador.nombre, administrador.correo, administrador.contrasena, administrador.telefono, administrador.id_usuario)
            filas = cursor.rowcount
            conexion.commit()
        return filas > 0

    def eliminar(self, idUsuario):
        with closing(self._conectar()) as conexion:
            cursor = conexion.cursor()
            cursor.execute("DELETE FROM Administrador WHERE id_usuario = ?", idUsuario)
            filas = cursor.rowcount
            conexion.commit()
        return filas > 0

    def listar(self):
        sql = "SELECT " + _COLUMNAS + " FROM Administrador ORDER BY id_usuario"
        with closing(self._conectar()) as conexion:
            filas = conexion.cursor().execute(sql).fetchall()
        return [Administrador(*fila) for fila in filas]

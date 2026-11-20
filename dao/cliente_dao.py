"""DAO de Cliente: único objeto que accede a la tabla Cliente."""
from contextlib import closing

import pyodbc

from entidades.cliente import Cliente

_COLUMNAS = "id_usuario, nombre, correo, contrasena, telefono, rol"


class ClienteDAO:
    def __init__(self, conexion):
        self._conexion = conexion

    def _conectar(self):
        return pyodbc.connect(self._conexion.obtener())

    def guardar(self, cliente):
        sql = ("INSERT INTO Cliente (nombre, correo, contrasena, telefono, rol) "
               "OUTPUT INSERTED.id_usuario VALUES (?, ?, ?, ?, ?)")
        with closing(self._conectar()) as conexion:
            cursor = conexion.cursor()
            cursor.execute(sql, cliente.nombre, cliente.correo, cliente.contrasena, cliente.telefono, cliente.rol)
            cliente.id_usuario = int(cursor.fetchone()[0])
            conexion.commit()
        return cliente.id_usuario

    def buscarPorId(self, idUsuario):
        sql = "SELECT " + _COLUMNAS + " FROM Cliente WHERE id_usuario = ?"
        with closing(self._conectar()) as conexion:
            fila = conexion.cursor().execute(sql, idUsuario).fetchone()
        return Cliente(*fila) if fila else None

    def actualizar(self, cliente):
        sql = "UPDATE Cliente SET nombre = ?, correo = ?, contrasena = ?, telefono = ? WHERE id_usuario = ?"
        with closing(self._conectar()) as conexion:
            cursor = conexion.cursor()
            cursor.execute(sql, cliente.nombre, cliente.correo, cliente.contrasena, cliente.telefono, cliente.id_usuario)
            filas = cursor.rowcount
            conexion.commit()
        return filas > 0

    def eliminar(self, idUsuario):
        with closing(self._conectar()) as conexion:
            cursor = conexion.cursor()
            cursor.execute("DELETE FROM Cliente WHERE id_usuario = ?", idUsuario)
            filas = cursor.rowcount
            conexion.commit()
        return filas > 0

    def listar(self):
        sql = "SELECT " + _COLUMNAS + " FROM Cliente ORDER BY id_usuario"
        with closing(self._conectar()) as conexion:
            filas = conexion.cursor().execute(sql).fetchall()
        return [Cliente(*fila) for fila in filas]

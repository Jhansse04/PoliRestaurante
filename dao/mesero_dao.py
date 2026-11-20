"""DAO de Mesero: único objeto que accede a la tabla Mesero."""
from contextlib import closing

import pyodbc

from entidades.mesero import Mesero

_COLUMNAS = "id_usuario, nombre, correo, contrasena, telefono, rol"


class MeseroDAO:
    def __init__(self, conexion):
        self._conexion = conexion

    def _conectar(self):
        return pyodbc.connect(self._conexion.obtener())

    def guardar(self, mesero):
        sql = ("INSERT INTO Mesero (nombre, correo, contrasena, telefono, rol) "
               "OUTPUT INSERTED.id_usuario VALUES (?, ?, ?, ?, ?)")
        with closing(self._conectar()) as conexion:
            cursor = conexion.cursor()
            cursor.execute(sql, mesero.nombre, mesero.correo, mesero.contrasena, mesero.telefono, mesero.rol)
            mesero.id_usuario = int(cursor.fetchone()[0])
            conexion.commit()
        return mesero.id_usuario

    def buscarPorId(self, idUsuario):
        sql = "SELECT " + _COLUMNAS + " FROM Mesero WHERE id_usuario = ?"
        with closing(self._conectar()) as conexion:
            fila = conexion.cursor().execute(sql, idUsuario).fetchone()
        return Mesero(*fila) if fila else None

    def actualizar(self, mesero):
        sql = "UPDATE Mesero SET nombre = ?, correo = ?, contrasena = ?, telefono = ? WHERE id_usuario = ?"
        with closing(self._conectar()) as conexion:
            cursor = conexion.cursor()
            cursor.execute(sql, mesero.nombre, mesero.correo, mesero.contrasena, mesero.telefono, mesero.id_usuario)
            filas = cursor.rowcount
            conexion.commit()
        return filas > 0

    def eliminar(self, idUsuario):
        with closing(self._conectar()) as conexion:
            cursor = conexion.cursor()
            cursor.execute("DELETE FROM Mesero WHERE id_usuario = ?", idUsuario)
            filas = cursor.rowcount
            conexion.commit()
        return filas > 0

    def listar(self):
        sql = "SELECT " + _COLUMNAS + " FROM Mesero ORDER BY id_usuario"
        with closing(self._conectar()) as conexion:
            filas = conexion.cursor().execute(sql).fetchall()
        return [Mesero(*fila) for fila in filas]

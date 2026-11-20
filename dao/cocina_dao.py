"""DAO de Cocina: único objeto que accede a la tabla Cocina."""
from contextlib import closing

import pyodbc

from entidades.cocina import Cocina

_COLUMNAS = "id_usuario, nombre, correo, contrasena, telefono, rol"


class CocinaDAO:
    def __init__(self, conexion):
        self._conexion = conexion

    def _conectar(self):
        return pyodbc.connect(self._conexion.obtener())

    def guardar(self, cocina):
        sql = ("INSERT INTO Cocina (nombre, correo, contrasena, telefono, rol) "
               "OUTPUT INSERTED.id_usuario VALUES (?, ?, ?, ?, ?)")
        with closing(self._conectar()) as conexion:
            cursor = conexion.cursor()
            cursor.execute(sql, cocina.nombre, cocina.correo, cocina.contrasena, cocina.telefono, cocina.rol)
            cocina.id_usuario = int(cursor.fetchone()[0])
            conexion.commit()
        return cocina.id_usuario

    def buscarPorId(self, idUsuario):
        sql = "SELECT " + _COLUMNAS + " FROM Cocina WHERE id_usuario = ?"
        with closing(self._conectar()) as conexion:
            fila = conexion.cursor().execute(sql, idUsuario).fetchone()
        return Cocina(*fila) if fila else None

    def actualizar(self, cocina):
        sql = "UPDATE Cocina SET nombre = ?, correo = ?, contrasena = ?, telefono = ? WHERE id_usuario = ?"
        with closing(self._conectar()) as conexion:
            cursor = conexion.cursor()
            cursor.execute(sql, cocina.nombre, cocina.correo, cocina.contrasena, cocina.telefono, cocina.id_usuario)
            filas = cursor.rowcount
            conexion.commit()
        return filas > 0

    def eliminar(self, idUsuario):
        with closing(self._conectar()) as conexion:
            cursor = conexion.cursor()
            cursor.execute("DELETE FROM Cocina WHERE id_usuario = ?", idUsuario)
            filas = cursor.rowcount
            conexion.commit()
        return filas > 0

    def listar(self):
        sql = "SELECT " + _COLUMNAS + " FROM Cocina ORDER BY id_usuario"
        with closing(self._conectar()) as conexion:
            filas = conexion.cursor().execute(sql).fetchall()
        return [Cocina(*fila) for fila in filas]

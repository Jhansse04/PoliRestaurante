"""DAO de Mesa: único objeto que accede a la tabla Mesa."""
from contextlib import closing

import pyodbc

from entidades.mesa import Mesa

_COLUMNAS = "id_mesa, numero, capacidad, estado"


class MesaDAO:
    def __init__(self, conexion):
        self._conexion = conexion

    def _conectar(self):
        return pyodbc.connect(self._conexion.obtener())

    def buscarPorId(self, idMesa):
        sql = "SELECT " + _COLUMNAS + " FROM Mesa WHERE id_mesa = ?"
        with closing(self._conectar()) as conexion:
            fila = conexion.cursor().execute(sql, idMesa).fetchone()
        return Mesa(*fila) if fila else None

    def listar(self):
        sql = "SELECT " + _COLUMNAS + " FROM Mesa ORDER BY numero"
        with closing(self._conectar()) as conexion:
            filas = conexion.cursor().execute(sql).fetchall()
        return [Mesa(*fila) for fila in filas]

    def actualizarMesa(self, mesa):
        sql = "UPDATE Mesa SET numero = ?, capacidad = ?, estado = ? WHERE id_mesa = ?"
        with closing(self._conectar()) as conexion:
            cursor = conexion.cursor()
            cursor.execute(sql, mesa.numero, mesa.capacidad, mesa.estado, mesa.id_mesa)
            filas = cursor.rowcount
            conexion.commit()
        return filas > 0

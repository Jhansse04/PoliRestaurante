"""DAO de Producto: único objeto que accede a la tabla Producto."""
from contextlib import closing

import pyodbc

from entidades.producto import Producto

_COLUMNAS = "id_producto, nombre, descripcion, precio, tipo, imagen, disponible"


class ProductoDAO:
    def __init__(self, conexion):
        self._conexion = conexion

    def _conectar(self):
        return pyodbc.connect(self._conexion.obtener())

    def guardar(self, producto):
        sql = ("INSERT INTO Producto (nombre, descripcion, precio, tipo, imagen, disponible) "
               "OUTPUT INSERTED.id_producto VALUES (?, ?, ?, ?, ?, ?)")
        with closing(self._conectar()) as conexion:
            cursor = conexion.cursor()
            cursor.execute(sql, producto.nombre, producto.descripcion, producto.precio,
                           producto.tipo, producto.imagen, producto.disponible)
            producto.id_producto = int(cursor.fetchone()[0])
            conexion.commit()
        return producto.id_producto

    def buscarPorId(self, idProducto):
        sql = "SELECT " + _COLUMNAS + " FROM Producto WHERE id_producto = ?"
        with closing(self._conectar()) as conexion:
            fila = conexion.cursor().execute(sql, idProducto).fetchone()
        return Producto(*fila) if fila else None

    def actualizar(self, producto):
        sql = ("UPDATE Producto SET nombre = ?, descripcion = ?, precio = ?, tipo = ?, imagen = ?, "
               "disponible = ? WHERE id_producto = ?")
        with closing(self._conectar()) as conexion:
            cursor = conexion.cursor()
            cursor.execute(sql, producto.nombre, producto.descripcion, producto.precio, producto.tipo,
                           producto.imagen, producto.disponible, producto.id_producto)
            filas = cursor.rowcount
            conexion.commit()
        return filas > 0

    def eliminar(self, idProducto):
        with closing(self._conectar()) as conexion:
            cursor = conexion.cursor()
            cursor.execute("DELETE FROM Producto WHERE id_producto = ?", idProducto)
            filas = cursor.rowcount
            conexion.commit()
        return filas > 0

    def listar(self):
        sql = "SELECT " + _COLUMNAS + " FROM Producto ORDER BY tipo, nombre"
        with closing(self._conectar()) as conexion:
            filas = conexion.cursor().execute(sql).fetchall()
        return [Producto(*fila) for fila in filas]

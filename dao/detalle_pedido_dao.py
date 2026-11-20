"""DAO de DetallePedido: único objeto que accede a la tabla DetallePedido."""
from contextlib import closing

import pyodbc

from entidades.detalle_pedido import DetallePedido

_COLUMNAS = "id_pedido, id_producto, cantidad, precio_unitario"


class DetallePedidoDAO:
    def __init__(self, conexion):
        self._conexion = conexion

    def _conectar(self):
        return pyodbc.connect(self._conexion.obtener())

    def guardar(self, detalle):
        sql = "INSERT INTO DetallePedido (id_pedido, id_producto, cantidad, precio_unitario) VALUES (?, ?, ?, ?)"
        with closing(self._conectar()) as conexion:
            conexion.cursor().execute(sql, detalle.id_pedido, detalle.id_producto,
                                      detalle.cantidad, detalle.precio_unitario)
            conexion.commit()
        return detalle

    def buscarPorPedido(self, idPedido):
        sql = "SELECT " + _COLUMNAS + " FROM DetallePedido WHERE id_pedido = ? ORDER BY id_producto"
        with closing(self._conectar()) as conexion:
            filas = conexion.cursor().execute(sql, idPedido).fetchall()
        return [DetallePedido(*fila) for fila in filas]

    def eliminar(self, idPedido):
        """Elimina todos los detalles del pedido indicado."""
        with closing(self._conectar()) as conexion:
            cursor = conexion.cursor()
            cursor.execute("DELETE FROM DetallePedido WHERE id_pedido = ?", idPedido)
            filas = cursor.rowcount
            conexion.commit()
        return filas > 0

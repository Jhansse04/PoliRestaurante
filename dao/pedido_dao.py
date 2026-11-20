"""DAO de Pedido: único objeto que accede a la tabla Pedido."""
from contextlib import closing

import pyodbc

from entidades import ROL_CLIENTE, ROL_COCINA, ROL_MESERO
from entidades.pedido import Pedido

_COLUMNAS = ("id_pedido, id_mesero, id_cocina, id_cliente, id_mesa, fecha, fecha_estado, "
             "tipo_pedido, direccion, estado, pagado, medio_pago, total")
_SELECT = "SELECT " + _COLUMNAS + " FROM Pedido"
_COLUMNA_POR_ROL = {ROL_MESERO: "id_mesero", ROL_COCINA: "id_cocina", ROL_CLIENTE: "id_cliente"}


class PedidoDAO:
    def __init__(self, conexion):
        self._conexion = conexion

    def _conectar(self):
        return pyodbc.connect(self._conexion.obtener())

    def _consultar(self, sql, *parametros):
        with closing(self._conectar()) as conexion:
            filas = conexion.cursor().execute(sql, *parametros).fetchall()
        return [Pedido(*fila) for fila in filas]

    def guardar(self, pedido):
        sql = ("INSERT INTO Pedido (id_mesero, id_cocina, id_cliente, id_mesa, fecha, fecha_estado, "
               "tipo_pedido, direccion, estado, pagado, medio_pago, total) "
               "OUTPUT INSERTED.id_pedido VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)")
        with closing(self._conectar()) as conexion:
            cursor = conexion.cursor()
            cursor.execute(sql, pedido.id_mesero, pedido.id_cocina, pedido.id_cliente, pedido.id_mesa,
                           pedido.fecha, pedido.fecha_estado, pedido.tipo_pedido, pedido.direccion,
                           pedido.estado, pedido.pagado, pedido.medio_pago, pedido.total)
            pedido.id_pedido = int(cursor.fetchone()[0])
            conexion.commit()
        return pedido.id_pedido

    def buscarPorId(self, idPedido):
        pedidos = self._consultar(_SELECT + " WHERE id_pedido = ?", idPedido)
        return pedidos[0] if pedidos else None

    def actualizarEstado(self, idPedido, estado, fechaEstado, estadoEsperado=None):
        """Actualiza el estado. Si se indica estadoEsperado solo actualiza cuando el pedido
        todavía está en ese estado (evita carreras entre cocina, mesero y cliente).
        Devuelve True si se modificó una fila."""
        sql = "UPDATE Pedido SET estado = ?, fecha_estado = ? WHERE id_pedido = ?"
        parametros = [estado, fechaEstado, idPedido]
        if estadoEsperado is not None:
            sql += " AND estado = ?"
            parametros.append(estadoEsperado)
        with closing(self._conectar()) as conexion:
            cursor = conexion.cursor()
            cursor.execute(sql, *parametros)
            filas = cursor.rowcount
            conexion.commit()
        return filas > 0

    def actualizarPago(self, idPedido, pagado, medioPago):
        sql = "UPDATE Pedido SET pagado = ?, medio_pago = ? WHERE id_pedido = ?"
        with closing(self._conectar()) as conexion:
            cursor = conexion.cursor()
            cursor.execute(sql, pagado, medioPago, idPedido)
            filas = cursor.rowcount
            conexion.commit()
        return filas > 0

    def eliminar(self, idPedido):
        with closing(self._conectar()) as conexion:
            cursor = conexion.cursor()
            cursor.execute("DELETE FROM Pedido WHERE id_pedido = ?", idPedido)
            filas = cursor.rowcount
            conexion.commit()
        return filas > 0

    def listarPorUsuario(self, rol, idUsuario):
        columna = _COLUMNA_POR_ROL.get(rol)
        if columna is None:
            raise ValueError("El rol %s no tiene pedidos asociados" % rol)
        return self._consultar(_SELECT + " WHERE " + columna + " = ? ORDER BY fecha DESC", idUsuario)

    def listarPorEstado(self, estados):
        if isinstance(estados, str):
            estados = [estados]
        estados = list(estados)
        if not estados:
            return []
        marcas = ", ".join("?" for _ in estados)
        return self._consultar(_SELECT + " WHERE estado IN (" + marcas + ") ORDER BY fecha DESC", *estados)

    def listar(self):
        return self._consultar(_SELECT + " ORDER BY fecha DESC")

    def listarPorMesa(self, idMesa):
        return self._consultar(_SELECT + " WHERE id_mesa = ? ORDER BY fecha DESC", idMesa)

    def listarPorFecha(self, desde, hasta):
        return self._consultar(_SELECT + " WHERE fecha >= ? AND fecha <= ? ORDER BY fecha DESC", desde, hasta)

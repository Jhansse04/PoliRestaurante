"""Capa DAO / PERSISTENCIA: los únicos objetos que interactúan con la base de datos."""
from dao.administrador_dao import AdministradorDAO
from dao.cliente_dao import ClienteDAO
from dao.cocina_dao import CocinaDAO
from dao.conexion import ConexionPorRol
from dao.detalle_pedido_dao import DetallePedidoDAO
from dao.mesa_dao import MesaDAO
from dao.mesero_dao import MeseroDAO
from dao.pedido_dao import PedidoDAO
from dao.producto_dao import ProductoDAO

__all__ = ["AdministradorDAO", "ClienteDAO", "CocinaDAO", "ConexionPorRol", "DetallePedidoDAO",
           "MesaDAO", "MeseroDAO", "PedidoDAO", "ProductoDAO"]

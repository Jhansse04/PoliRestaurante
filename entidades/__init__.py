"""Capa de ENTIDADES (modelo de MVC)."""
from entidades.administrador import Administrador, ROL as ROL_ADMINISTRADOR
from entidades.cliente import Cliente, ROL as ROL_CLIENTE
from entidades.cocina import Cocina, ROL as ROL_COCINA
from entidades.detalle_pedido import DetallePedido
from entidades.mesa import Mesa
from entidades.mesero import Mesero, ROL as ROL_MESERO
from entidades.pedido import Pedido
from entidades.producto import Producto

ROLES = (ROL_ADMINISTRADOR, ROL_MESERO, ROL_COCINA, ROL_CLIENTE)

__all__ = [
    "Administrador", "Cliente", "Cocina", "DetallePedido", "Mesa", "Mesero", "Pedido", "Producto",
    "ROL_ADMINISTRADOR", "ROL_MESERO", "ROL_COCINA", "ROL_CLIENTE", "ROLES",
]

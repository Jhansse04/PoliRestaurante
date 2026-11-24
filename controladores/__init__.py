"""Capa CONTROLADORES (MVC): reciben la solicitud de la vista y la delegan en los Managers."""
from controladores.administrador_controller import AdministradorController
from controladores.pedido_controller import PedidoController
from controladores.producto_controller import ProductoController
from controladores.usuario_controller import RUTAS_POR_ROL, UsuarioController

__all__ = ["PedidoController", "ProductoController", "UsuarioController",
           "AdministradorController", "RUTAS_POR_ROL"]

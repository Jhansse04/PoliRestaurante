"""OBSERVER: propagación de cambios de estado de los pedidos."""
from observadores.administrador_observer import AdministradorObserver
from observadores.canal_tiempo_real import CanalTiempoReal
from observadores.cliente_observer import ClienteObserver
from observadores.cocina_observer import CocinaObserver
from observadores.mesero_observer import MeseroObserver
from observadores.pedido_observer import PedidoObserver

__all__ = ["PedidoObserver", "CocinaObserver", "MeseroObserver", "ClienteObserver",
           "AdministradorObserver", "CanalTiempoReal"]

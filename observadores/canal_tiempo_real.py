"""CanalTiempoReal: transporta las notificaciones a las vistas (WebSocket vía Flask-SocketIO).

`destino` es el nombre de la sala a la que se suscribe cada vista al conectarse:
"cocina", "mesero", "administrador" o "cliente:<id_usuario>".
"""
import json

NOMBRE_EVENTO_SOCKET = "pedido"


class CanalTiempoReal:
    def __init__(self, socketio):
        self._socketio = socketio

    def enviar(self, destino, mensaje):
        # Se convierte a JSON puro (Decimal y datetime pasan a texto).
        carga = json.loads(json.dumps(mensaje, default=str))
        self._socketio.emit(NOMBRE_EVENTO_SOCKET, carga, to=destino)

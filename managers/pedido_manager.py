"""PedidoManager: lógica de negocio de los pedidos.

* Selecciona la fábrica según tipo_pedido, valida las reglas generales y persiste (Factory).
* Es el sujeto/publicador del Observer: notifica DESPUÉS de que la persistencia confirma el cambio.
* Las operaciones reciben el rol y el id del usuario de la sesión confiable (los pone el controlador,
  nunca el cliente), de modo que las reglas "por rol" se aplican aquí.
"""
import logging
from datetime import datetime, timedelta

from entidades import ROL_CLIENTE, ROL_COCINA, ROL_MESERO
from entidades.detalle_pedido import DetallePedido
from entidades.pedido import (ESTADO_CANCELADO, ESTADO_EN_PREPARACION, ESTADO_ENTREGADO, ESTADO_LISTO,
                              ESTADO_PENDIENTE, ESTADOS, TIPO_MESA)
from observadores.pedido_observer import (EVENTO_ESTADO_CAMBIADO, EVENTO_PEDIDO_CANCELADO,
                                          EVENTO_PEDIDO_CREADO)

_registro = logging.getLogger(__name__)

_FUERA_DE_ALCANCE = "Funcionalidad fuera del alcance de las 15 historias de usuario"

MAX_CANTIDAD_POR_PRODUCTO = 99
HORAS_PEDIDOS_RECIENTES = 24  # HU12: "pedidos activos y recientes"
ESTADOS_ACTIVOS = (ESTADO_PENDIENTE, ESTADO_EN_PREPARACION, ESTADO_LISTO)

# HU08 / HU13: el estado solo avanza, de a un paso.
_SIGUIENTE_ESTADO = {
    ESTADO_PENDIENTE: ESTADO_EN_PREPARACION,
    ESTADO_EN_PREPARACION: ESTADO_LISTO,
    ESTADO_LISTO: ESTADO_ENTREGADO,
}
# Rol que puede llevar un pedido a cada estado (cocina prepara, mesero entrega).
_ROL_QUE_APLICA = {
    ESTADO_EN_PREPARACION: ROL_COCINA,
    ESTADO_LISTO: ROL_COCINA,
    ESTADO_ENTREGADO: ROL_MESERO,
}
# HU05 / HU15: estados desde los que cada rol puede cancelar.
_CANCELABLE_POR_ROL = {
    ROL_MESERO: (ESTADO_PENDIENTE, ESTADO_EN_PREPARACION),
    ROL_CLIENTE: (ESTADO_PENDIENTE,),
}


class PedidoManager:
    def __init__(self, pedidoDAO, detallePedidoDAO, mesaDAO, productoManager, usuarioManager, fabricas):
        self._pedidoDAO = pedidoDAO
        self._detallePedidoDAO = detallePedidoDAO
        self._mesaDAO = mesaDAO
        self._productoManager = productoManager
        self._usuarioManager = usuarioManager
        self._fabricas = fabricas  # {tipo_pedido: PedidoFactory}
        self._observadores = []

    # ------------------------------------------------------------------ Observer
    def suscribir(self, observer):
        if observer not in self._observadores:
            self._observadores.append(observer)

    def desuscribir(self, observer):
        if observer in self._observadores:
            self._observadores.remove(observer)

    def notificarCambio(self, pedido, evento):
        for observador in list(self._observadores):
            try:
                observador.actualizar(pedido, evento)
            except Exception:  # un observador caído no debe deshacer una operación ya persistida
                _registro.exception("El observador %s falló al procesar %s", type(observador).__name__, evento)

    # ------------------------------------------------------- HU03 / HU10: crear pedido
    def crearPedido(self, datos, rol, idUsuario):
        self._exigirRol(rol, ROL_MESERO, ROL_CLIENTE)
        if not isinstance(datos, dict):
            raise ValueError("Los datos del pedido deben enviarse como un objeto JSON")

        tipo = str(datos.get("tipo_pedido") or "").strip().upper()
        if tipo not in self._fabricas:
            raise ValueError({"error": "Los datos del pedido no son válidos",
                              "campos": {"tipo_pedido": "Debe ser MESA o DOMICILIO"}})
        if (rol == ROL_MESERO) != (tipo == TIPO_MESA):
            raise PermissionError("El mesero solo registra pedidos de mesa y el cliente solo pedidos a domicilio")

        errores = {}
        lineas, total = self._validarItems(datos.get("items"), errores)
        cocina = self._asignarCocina()

        idCliente = idUsuario if rol == ROL_CLIENTE else self._entero(datos.get("id_cliente"))
        mesa = None
        if tipo == TIPO_MESA:
            idMesa = self._entero(datos.get("id_mesa"))
            mesa = self._mesaDAO.buscarPorId(idMesa) if idMesa is not None else None
            if idCliente is not None and not self._existeCliente(idCliente):
                errores["id_cliente"] = "El cliente indicado no existe"

        datosFabrica = {
            "tipo_pedido": tipo,
            "id_cliente": idCliente,
            "id_cocina": cocina.id_usuario,
            "id_mesero": idUsuario if rol == ROL_MESERO else None,
            "mesa": mesa,
            "direccion": datos.get("direccion"),
            "total": total,
        }
        pedido = None
        try:
            pedido = self._fabricas[tipo].crearPedido(datosFabrica)
        except ValueError as error:
            errores.update(self._camposDe(error))
        if errores:
            raise ValueError({"error": "Los datos del pedido no son válidos", "campos": errores})

        # Persistencia: encabezado y luego detalles; si algo falla se compensa para no dejar huérfanos.
        self._pedidoDAO.guardar(pedido)
        try:
            for linea in lineas:
                linea.id_pedido = pedido.id_pedido
                self._detallePedidoDAO.guardar(linea)
        except Exception:
            self._compensar(pedido.id_pedido)
            raise

        self.notificarCambio(pedido, EVENTO_PEDIDO_CREADO)
        resultado = self._componer(pedido, rol, idUsuario, {})
        resultado["mensaje"] = "Pedido creado correctamente"
        return resultado

    # --------------------------------------------- HU04 / HU09 / HU11: consultar un pedido
    def obtenerPedido(self, idPedido, rol, idUsuario):
        self._exigirRol(rol, ROL_MESERO, ROL_COCINA, ROL_CLIENTE)
        pedido = self._buscarVisible(idPedido, rol, idUsuario)
        return self._componer(pedido, rol, idUsuario, {})

    # ------------------------------------------------ HU07 / HU13 / HU11: listar pedidos
    def obtenerPedidos(self, rol, idUsuario):
        self._exigirRol(rol, ROL_MESERO, ROL_COCINA, ROL_CLIENTE)
        if rol == ROL_COCINA:  # pedidos por atender, el más antiguo primero
            pedidos = sorted(self._pedidoDAO.listarPorEstado(ESTADOS_ACTIVOS), key=lambda p: p.fecha)
        elif rol == ROL_MESERO:  # HU13: todos los pedidos
            pedidos = self._pedidoDAO.listar()
        else:  # cliente: solo los suyos
            pedidos = self._pedidoDAO.listarPorUsuario(ROL_CLIENTE, idUsuario)
        return self._componerLista(pedidos, rol, idUsuario)

    # -------------------------------------------------- HU05 / HU15: cancelar un pedido
    def cancelarPedido(self, idPedido, rol, idUsuario, confirmar=False):
        self._exigirRol(rol, ROL_MESERO, ROL_CLIENTE)
        pedido = self._buscarVisible(idPedido, rol, idUsuario)
        if pedido.estado == ESTADO_CANCELADO:
            raise ValueError("El pedido ya fue cancelado")
        if pedido.estado not in _CANCELABLE_POR_ROL[rol]:
            if rol == ROL_CLIENTE:
                raise ValueError("La cancelación no está disponible: el pedido ya está en preparación "
                                 "o fue enviado (estado actual: %s)" % pedido.estado)
            raise ValueError("No se puede cancelar un pedido en estado %s" % pedido.estado)

        if rol == ROL_CLIENTE and not confirmar:  # HU15 escenario 2: pedir confirmación
            return {"requiere_confirmacion": True, "id_pedido": pedido.id_pedido,
                    "mensaje": "¿Confirma que desea cancelar el pedido #%s?" % pedido.id_pedido}

        ahora = datetime.now().replace(microsecond=0)
        if not self._pedidoDAO.actualizarEstado(pedido.id_pedido, ESTADO_CANCELADO, ahora,
                                                estadoEsperado=pedido.estado):
            raise ValueError("El pedido cambió de estado mientras se procesaba la solicitud; consúltelo de nuevo")
        pedido.estado = ESTADO_CANCELADO
        pedido.fecha_estado = ahora

        self.notificarCambio(pedido, EVENTO_PEDIDO_CANCELADO)
        resultado = self._componer(pedido, rol, idUsuario, {})
        resultado["mensaje"] = "El pedido #%s fue cancelado correctamente" % pedido.id_pedido
        return resultado

    # ------------------------------------------------ HU08 / HU13: actualizar el estado
    def actualizarEstado(self, idPedido, nuevoEstado, rol, idUsuario):
        self._exigirRol(rol, ROL_COCINA, ROL_MESERO)
        nuevoEstado = str(nuevoEstado or "").strip().upper().replace("_", " ")
        if nuevoEstado not in ESTADOS:
            raise ValueError("Estado inválido. Estados permitidos: " + ", ".join(ESTADOS))

        pedido = self._buscarVisible(idPedido, rol, idUsuario)
        if pedido.estado == ESTADO_CANCELADO:
            raise ValueError("El pedido fue cancelado; no se puede cambiar su estado")
        if nuevoEstado == ESTADO_CANCELADO:
            raise ValueError("Para cancelar un pedido use la opción 'Cancelar pedido'")
        if nuevoEstado == pedido.estado:
            raise ValueError("El pedido ya se encuentra en estado %s" % pedido.estado)

        siguiente = _SIGUIENTE_ESTADO.get(pedido.estado)
        if siguiente is None:
            raise ValueError("El pedido ya fue entregado; su estado no puede cambiar")
        if nuevoEstado != siguiente:
            raise ValueError("El estado del pedido no se puede retroceder. Desde %s solo se permite "
                             "avanzar a %s" % (pedido.estado, siguiente))
        if _ROL_QUE_APLICA[nuevoEstado] != rol:
            raise PermissionError("El rol %s no puede cambiar un pedido a %s" % (rol, nuevoEstado))

        ahora = datetime.now().replace(microsecond=0)
        if not self._pedidoDAO.actualizarEstado(pedido.id_pedido, nuevoEstado, ahora,
                                                estadoEsperado=pedido.estado):
            raise ValueError("El pedido cambió de estado mientras se procesaba la solicitud; consúltelo de nuevo")
        pedido.estado = nuevoEstado
        pedido.fecha_estado = ahora

        self.notificarCambio(pedido, EVENTO_ESTADO_CAMBIADO)
        resultado = self._componer(pedido, rol, idUsuario, {})
        resultado["mensaje"] = "Operación exitosa"
        return resultado

    # ------------------------------------------------------------ HU13: marcar entregado
    def marcarComoEntregado(self, idPedido, rol, idUsuario):
        return self.actualizarEstado(idPedido, ESTADO_ENTREGADO, rol, idUsuario)

    # -------------------------------------------------- HU06 / HU11: historial de pedidos
    def consultarHistorial(self, rol, idUsuario):
        self._exigirRol(rol, ROL_MESERO, ROL_CLIENTE)
        pedidos = self._pedidoDAO.listarPorUsuario(rol, idUsuario)
        return self._componerLista(pedidos, rol, idUsuario)

    # ------------------------------------------------------------ HU12: panel general
    def obtenerPanelGlobal(self, filtros=None):
        ahora = datetime.now().replace(microsecond=0)
        activos = self._pedidoDAO.listarPorEstado(ESTADOS_ACTIVOS)
        recientes = self._pedidoDAO.listarPorFecha(ahora - timedelta(hours=HORAS_PEDIDOS_RECIENTES), ahora)
        unicos = {p.id_pedido: p for p in activos + recientes}
        pedidos = sorted(unicos.values(), key=lambda p: p.fecha, reverse=True)
        return self._componerLista(pedidos, None, None)

    # ----------------------------- Operaciones del diagrama que ninguna HU requiere
    def marcarComoPagado(self, idPedido, rol, idUsuario):
        raise NotImplementedError(_FUERA_DE_ALCANCE)

    def consultarPedidosPorMesa(self, idMesa, rol, idUsuario):
        raise NotImplementedError(_FUERA_DE_ALCANCE)

    def consultarPedidosPorFecha(self, desde, hasta, rol, idUsuario):
        raise NotImplementedError(_FUERA_DE_ALCANCE)

    # ================================================================== auxiliares
    @staticmethod
    def _exigirRol(rol, *permitidos):
        if rol not in permitidos:
            raise PermissionError("Su rol no tiene permiso para realizar esta operación")

    def _buscarVisible(self, idPedido, rol, idUsuario):
        """Devuelve el pedido o LookupError. Un cliente solo ve los suyos (el resto 'no es válido')."""
        pedido = self._pedidoDAO.buscarPorId(idPedido)
        if pedido is None or (rol == ROL_CLIENTE and pedido.id_cliente != idUsuario):
            raise LookupError("El pedido no es válido")
        return pedido

    @staticmethod
    def _entero(valor):
        if isinstance(valor, bool):
            return None
        if isinstance(valor, int):
            return valor
        if isinstance(valor, str) and valor.strip().isdigit():
            return int(valor.strip())
        return None

    @staticmethod
    def _camposDe(error):
        contenido = error.args[0] if error.args else None
        if isinstance(contenido, dict):
            return contenido.get("campos") or {"pedido": contenido.get("error", "Datos inválidos")}
        return {"pedido": str(error)}

    def _validarItems(self, items, errores):
        """Valida los productos pedidos. Devuelve (detalles, total); acumula mensajes en errores['items']."""
        if not isinstance(items, list) or not items:
            errores["items"] = "Debe incluir al menos un producto"
            return [], 0
        problemas, cantidades = [], {}
        for posicion, item in enumerate(items, start=1):
            idProducto = self._entero(item.get("id_producto")) if isinstance(item, dict) else None
            cantidad = self._entero(item.get("cantidad")) if isinstance(item, dict) else None
            if idProducto is None:
                problemas.append("ítem %d: id_producto inválido" % posicion)
            elif cantidad is None or not 1 <= cantidad <= MAX_CANTIDAD_POR_PRODUCTO:
                problemas.append("ítem %d: la cantidad debe ser un entero entre 1 y %d"
                                 % (posicion, MAX_CANTIDAD_POR_PRODUCTO))
            else:
                cantidades[idProducto] = cantidades.get(idProducto, 0) + cantidad

        lineas, total = [], 0
        for idProducto, cantidad in cantidades.items():
            try:
                producto = self._productoManager.consultarProducto(idProducto)
            except LookupError:
                problemas.append("el producto %d no existe" % idProducto)
                continue
            if not producto.disponible:
                problemas.append("el producto '%s' no está disponible" % producto.nombre)
                continue
            lineas.append(DetallePedido(None, idProducto, cantidad, producto.precio))  # precio vigente al pedir
            total += producto.precio * cantidad
        if problemas:
            errores["items"] = "; ".join(problemas)
        return lineas, total

    def _asignarCocina(self):
        cocinas = self._usuarioManager.listarUsuarios(ROL_COCINA)
        if not cocinas:
            raise ValueError("No hay personal de cocina registrado para recibir pedidos")
        return cocinas[0]

    def _existeCliente(self, idCliente):
        try:
            self._usuarioManager.obtenerUsuario(idCliente, ROL_CLIENTE)
            return True
        except LookupError:
            return False

    def _compensar(self, idPedido):
        for descripcion, accion in (("detalles", self._detallePedidoDAO.eliminar),
                                    ("pedido", self._pedidoDAO.eliminar)):
            try:
                accion(idPedido)
            except Exception:
                _registro.exception("No se pudo revertir %s del pedido %s", descripcion, idPedido)

    @staticmethod
    def _cacheado(cache, clave, obtener):
        if clave not in cache:
            try:
                cache[clave] = obtener()
            except LookupError:
                cache[clave] = None
        return cache[clave]

    def _componerLista(self, pedidos, rol, idUsuario):
        cache = {}
        return [self._componer(p, rol, idUsuario, cache) for p in pedidos]

    def _componer(self, pedido, rol, idUsuario, cache):
        """Arma la vista completa de un pedido: encabezado, detalles, mesa, mesero y cliente."""
        lineas = []
        for detalle in self._detallePedidoDAO.buscarPorPedido(pedido.id_pedido):
            producto = self._cacheado(cache, ("producto", detalle.id_producto),
                                      lambda d=detalle: self._productoManager.consultarProducto(d.id_producto))
            lineas.append({
                "id_producto": detalle.id_producto,
                "producto": producto.nombre if producto else "Producto %s" % detalle.id_producto,
                "cantidad": detalle.cantidad,
                "precio_unitario": detalle.precio_unitario,
                "subtotal": detalle.precio_unitario * detalle.cantidad,
            })

        mesa = None
        if pedido.id_mesa is not None:
            mesa = self._cacheado(cache, ("mesa", pedido.id_mesa), lambda: self._mesaDAO.buscarPorId(pedido.id_mesa))
        mesero = None
        if pedido.id_mesero is not None:
            mesero = self._cacheado(cache, ("mesero", pedido.id_mesero),
                                    lambda: self._usuarioManager.obtenerUsuario(pedido.id_mesero, ROL_MESERO))
        cliente = None
        if pedido.id_cliente is not None:
            cliente = self._cacheado(cache, ("cliente", pedido.id_cliente),
                                     lambda: self._usuarioManager.obtenerUsuario(pedido.id_cliente, ROL_CLIENTE))

        if pedido.tipo_pedido == TIPO_MESA:
            origen = "Mesa %s" % mesa.numero if mesa else "Mesa"
            responsable = mesero.nombre if mesero else None
        else:
            origen = "Domicilio"
            responsable = cliente.nombre if cliente else None

        referencia = pedido.fecha_estado or pedido.fecha or datetime.now()
        segundos = max(0, int((datetime.now() - referencia).total_seconds()))

        mensaje = None
        if pedido.estado == ESTADO_CANCELADO:  # HU11 escenario 2 y HU13 escenario 5
            cuando = pedido.fecha_estado.strftime("%Y-%m-%d %H:%M:%S") if pedido.fecha_estado else "fecha desconocida"
            mensaje = "El pedido fue cancelado el %s" % cuando

        return {
            "id_pedido": pedido.id_pedido,
            "tipo_pedido": pedido.tipo_pedido,
            "estado": pedido.estado,
            "fecha": pedido.fecha,
            "fecha_estado": pedido.fecha_estado,
            "segundos_en_estado": segundos,
            "origen": origen,
            "responsable": responsable,
            "direccion": pedido.direccion,
            "mesa": {"id_mesa": mesa.id_mesa, "numero": mesa.numero} if mesa else None,
            "mesero": {"id_usuario": mesero.id_usuario, "nombre": mesero.nombre} if mesero else None,
            "cliente": {"id_usuario": cliente.id_usuario, "nombre": cliente.nombre} if cliente else None,
            "detalles": lineas,
            "total": pedido.total,
            "pagado": pedido.pagado,
            "medio_pago": pedido.medio_pago,
            "puede_cancelar": self._puedeCancelar(pedido, rol, idUsuario),
            "mensaje": mensaje,
        }

    @staticmethod
    def _puedeCancelar(pedido, rol, idUsuario):
        permitidos = _CANCELABLE_POR_ROL.get(rol)
        if not permitidos:
            return False
        if rol == ROL_CLIENTE and pedido.id_cliente != idUsuario:
            return False
        return pedido.estado in permitidos

"""ProductoManager: gestión del menú (HU01, HU02) y consulta de productos (HU14)."""
from decimal import Decimal, InvalidOperation

from entidades.producto import TIPOS, Producto

_FUERA_DE_ALCANCE = "Funcionalidad fuera del alcance de las 15 historias de usuario"
_CENTAVOS = Decimal("0.01")
_PRECIO_MAXIMO = Decimal("99999999.99")


class ProductoManager:
    def __init__(self, productoDAO):
        self._productoDAO = productoDAO

    # ---- HU01: crear producto ----
    def crearProducto(self, datos):
        limpios = self._validar(datos, parcial=False)
        producto = Producto(id_producto=None, **limpios)
        self._productoDAO.guardar(producto)
        return producto

    # ---- HU02: modificar producto (solo se cambian los campos enviados) ----
    def modificarProducto(self, idProducto, datos):
        limpios = self._validar(datos, parcial=True)
        producto = self.consultarProducto(idProducto)
        for campo, valor in limpios.items():
            setattr(producto, campo, valor)
        if not self._productoDAO.actualizar(producto):
            raise LookupError("El producto no existe")
        return producto

    def eliminarProducto(self, idProducto):
        raise NotImplementedError(_FUERA_DE_ALCANCE)

    # ---- HU14: consulta ----
    def consultarProducto(self, idProducto):
        producto = self._productoDAO.buscarPorId(idProducto)
        if producto is None:
            raise LookupError("El producto no existe")
        return producto

    def listarProductos(self, soloDisponibles=False):
        productos = self._productoDAO.listar()
        if soloDisponibles:
            productos = [p for p in productos if p.disponible]
        return productos

    def cambiarDisponibilidad(self, idProducto, disponible):
        return self.modificarProducto(idProducto, {"disponible": disponible})

    # ---- validación de datos ----
    def _validar(self, datos, parcial):
        if not isinstance(datos, dict):
            raise ValueError("Los datos del producto deben enviarse como un objeto JSON")
        errores, limpios = {}, {}

        def aplica(campo):
            return (not parcial) or (campo in datos)

        if aplica("nombre"):
            nombre = datos.get("nombre")
            if not isinstance(nombre, str) or not nombre.strip() or len(nombre.strip()) > 100:
                errores["nombre"] = "Es obligatorio y debe tener entre 1 y 100 caracteres"
            else:
                limpios["nombre"] = nombre.strip()

        if "descripcion" in datos:
            descripcion = datos["descripcion"]
            if descripcion is None or (isinstance(descripcion, str) and not descripcion.strip()):
                limpios["descripcion"] = None
            elif isinstance(descripcion, str) and len(descripcion.strip()) <= 2000:
                limpios["descripcion"] = descripcion.strip()
            else:
                errores["descripcion"] = "Debe ser texto de máximo 2000 caracteres"
        elif not parcial:
            limpios["descripcion"] = None

        if aplica("precio"):
            precio = self._aDecimal(datos.get("precio"))
            if precio is None or precio <= 0 or precio > _PRECIO_MAXIMO:
                errores["precio"] = "Debe ser un número mayor a 0, con máximo 2 decimales"
            else:
                limpios["precio"] = precio

        if aplica("tipo"):
            tipo = datos.get("tipo")
            tipo = tipo.strip().upper() if isinstance(tipo, str) else None
            if tipo not in TIPOS:
                errores["tipo"] = "Debe ser uno de: " + ", ".join(TIPOS)
            else:
                limpios["tipo"] = tipo

        if "imagen" in datos:
            imagen = datos["imagen"]
            if imagen is None or (isinstance(imagen, str) and not imagen.strip()):
                limpios["imagen"] = None
            elif isinstance(imagen, str) and len(imagen.strip()) <= 255:
                limpios["imagen"] = imagen.strip()
            else:
                errores["imagen"] = "Debe ser texto de máximo 255 caracteres"
        elif not parcial:
            limpios["imagen"] = None

        if "disponible" in datos:
            disponible = self._aBooleano(datos["disponible"])
            if disponible is None:
                errores["disponible"] = "Debe ser verdadero o falso"
            else:
                limpios["disponible"] = disponible
        elif not parcial:
            limpios["disponible"] = True

        if parcial and not datos:
            errores["datos"] = "Debe indicar al menos un campo a modificar"

        if errores:
            raise ValueError({"error": "Los datos del producto no son válidos", "campos": errores})
        return limpios

    @staticmethod
    def _aDecimal(valor):
        if isinstance(valor, bool) or not isinstance(valor, (int, float, str)):
            return None
        try:
            numero = Decimal(str(valor).strip())
            if not numero.is_finite():
                return None
            redondeado = numero.quantize(_CENTAVOS)
        except InvalidOperation:
            return None
        return redondeado if redondeado == numero else None  # rechaza más de 2 decimales

    @staticmethod
    def _aBooleano(valor):
        if isinstance(valor, bool):
            return valor
        if isinstance(valor, int) and valor in (0, 1):
            return bool(valor)
        if isinstance(valor, str):
            texto = valor.strip().lower()
            if texto in ("true", "1", "si", "sí"):
                return True
            if texto in ("false", "0", "no"):
                return False
        return None

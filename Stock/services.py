from dataclasses import dataclass
from decimal import Decimal
from typing import Iterable, Protocol

from django.db import transaction

from .models import MovimientosStock, Producto


class InventoryValidationError(ValueError):
    """Error de negocio que impide completar un movimiento de inventario."""


@dataclass(frozen=True)
class StockRequest:
    producto_id: int
    cantidad: int


class InventoryService(Protocol):
    def receive(self, requests: list[StockRequest], user_id: int, reference: str) -> None:
        ...

    def adjust(self, requests: list[StockRequest], user_id: int, reference: str) -> None:
        ...

    def transfer(self, requests: list[StockRequest], source_id: int, destination_id: int, user_id: int) -> None:
        ...


class SalesService(Protocol):
    def quote(self, customer_id: int, requests: list[StockRequest]) -> int:
        ...

    def confirm(self, quote_id: int, user_id: int) -> int:
        ...

    def cancel(self, sale_id: int, user_id: int) -> None:
        ...


class CashService(Protocol):
    def open_register(self, user_id: int, opening_amount: Decimal) -> int:
        ...

    def close_register(self, register_id: int, counted_amount: Decimal) -> Decimal:
        ...


class NotImplementedInventoryService:
    def receive(self, requests: list[StockRequest], user_id: int, reference: str) -> None:
        raise NotImplementedError

    def adjust(self, requests: list[StockRequest], user_id: int, reference: str) -> None:
        raise NotImplementedError

    def transfer(self, requests: list[StockRequest], source_id: int, destination_id: int, user_id: int) -> None:
        raise NotImplementedError


def _get_product_locked(producto_id):
    try:
        return Producto.objects.select_for_update().get(pk=producto_id)
    except Producto.DoesNotExist as exc:
        raise InventoryValidationError(f"El producto #{producto_id} no existe.") from exc


def _validate_quantity(cantidad):
    if not isinstance(cantidad, int) or isinstance(cantidad, bool) or cantidad <= 0:
        raise InventoryValidationError("La cantidad debe ser un entero mayor que cero.")


def _create_movement(producto, tipo, cantidad, usuario=None, referencia="", descripcion=""):
    return MovimientosStock.objects.create(
        producto=producto,
        tipo=tipo,
        cantidad=cantidad,
        saldo_resultante=producto.stock,
        usuario=usuario,
        referencia=referencia,
        descripcion=descripcion,
    )


@transaction.atomic
def registrar_entrada(producto_id, cantidad, usuario=None, referencia="", descripcion=""):
    """Suma stock y registra una entrada de inventario."""
    _validate_quantity(cantidad)
    producto = _get_product_locked(producto_id)
    producto.stock += cantidad
    producto.save(update_fields=["stock"])
    _create_movement(producto, "ENTRADA", cantidad, usuario, referencia, descripcion)
    return producto


@transaction.atomic
def ajuste_stock(producto_id, cantidad, usuario=None, referencia="", descripcion=""):
    """Aplica un ajuste firmado, rechazando cualquier resultado negativo."""
    if not isinstance(cantidad, int) or isinstance(cantidad, bool) or cantidad == 0:
        raise InventoryValidationError("El ajuste debe ser un entero distinto de cero.")

    producto = _get_product_locked(producto_id)
    nuevo_stock = producto.stock + cantidad
    if nuevo_stock < 0:
        raise InventoryValidationError(
            f"El ajuste dejaría el stock de '{producto.nombre}' en negativo."
        )
    producto.stock = nuevo_stock
    producto.save(update_fields=["stock"])
    _create_movement(
        producto,
        "AJUSTE" if cantidad > 0 else "MERMA",
        abs(cantidad),
        usuario,
        referencia,
        descripcion,
    )
    return producto


@transaction.atomic
def procesar_devolucion(
    producto_id,
    cantidad,
    usuario=None,
    precio_unitario=None,
    referencia="",
    descripcion="",
):
    """Reintegra unidades vendidas después de validar el precio vigente."""
    _validate_quantity(cantidad)
    producto = _get_product_locked(producto_id)
    if precio_unitario is not None and Decimal(str(precio_unitario)) != producto.precio:
        raise InventoryValidationError(
            f"El precio de devolución no coincide con el precio del producto '{producto.nombre}'."
        )
    producto.stock += cantidad
    producto.save(update_fields=["stock"])
    _create_movement(
        producto,
        "ENTRADA",
        cantidad,
        usuario,
        referencia,
        descripcion or "Devolución de venta",
    )
    return producto


@transaction.atomic
def procesar_venta(
    cliente,
    vendedor,
    detalles: Iterable[dict],
    telefono="",
    email="",
):
    """Crea una venta y descuenta todas sus líneas bajo el mismo bloqueo."""
    from ventas.models import Detalle_venta, Venta

    cantidades = {}
    for detalle in detalles:
        producto = detalle.get("producto")
        producto_id = producto.pk if producto is not None else detalle.get("producto_id")
        cantidad = detalle.get("cantidad")
        _validate_quantity(cantidad)
        if producto_id is None:
            raise InventoryValidationError("Cada línea debe indicar un producto.")
        cantidades[producto_id] = cantidades.get(producto_id, 0) + cantidad

    if not cantidades:
        raise InventoryValidationError("La venta debe contener al menos un producto.")

    productos = {
        producto.pk: producto
        for producto in Producto.objects.select_for_update().filter(pk__in=cantidades)
    }
    for producto_id, cantidad in cantidades.items():
        producto = productos.get(producto_id)
        if producto is None:
            raise InventoryValidationError(f"El producto #{producto_id} no existe.")
        if cantidad > producto.stock:
            raise InventoryValidationError(
                f"Sin stock suficiente para '{producto.nombre}'. "
                f"Solicitas {cantidad}, pero quedan {producto.stock}."
            )

    venta = Venta.objects.create(
        cliente=cliente,
        vendedor=vendedor,
        telefono=telefono,
        email=email,
    )
    total = Decimal("0")
    for producto_id, cantidad in cantidades.items():
        producto = productos[producto_id]
        producto.stock -= cantidad
        producto.save(update_fields=["stock"])
        Detalle_venta.objects.create(
            venta=venta,
            producto=producto,
            cantidad=cantidad,
            precio_unitario=producto.precio,
        )
        total += cantidad * producto.precio
        _create_movement(
            producto,
            "VENTA",
            cantidad,
            vendedor,
            f"Venta #{venta.pk}",
        )

    venta.total = total
    venta.save(update_fields=["total"])
    return venta
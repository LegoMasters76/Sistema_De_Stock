from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol


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
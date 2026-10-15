"""Modelo inmutable de órdenes Spot de referencia."""
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class PendingSpotOrder:
    symbol: str
    side: str
    quantity: Decimal
    limit_price: Decimal
    status: str = "UNVERIFIED"

    def __post_init__(self):
        if self.symbol not in {"BTCUSDT", "ETHUSDT", "WLDUSDT"}:
            raise ValueError("Activo no autorizado para seguimiento")
        if self.side not in {"BUY", "SELL"}:
            raise ValueError("Lado inválido")
        if not self.quantity.is_finite() or self.quantity <= 0:
            raise ValueError("Cantidad inválida")
        if not self.limit_price.is_finite() or self.limit_price <= 0:
            raise ValueError("Precio límite inválido")
        if self.status != "UNVERIFIED":
            raise ValueError("Sin API privada no se puede verificar estado real")

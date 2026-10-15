"""Evaluación explicable sin recomendación ni automatización de órdenes."""
from decimal import Decimal
from typing import Any

from bot.orders.models import PendingSpotOrder


def review_pending_order(order: PendingSpotOrder, analysis: dict[str, Any]) -> dict[str, Any]:
    if analysis.get("symbol") != order.symbol:
        raise ValueError("Análisis y orden corresponden a activos diferentes")
    if analysis.get("source") != "BINANCE_PUBLIC_REST":
        raise ValueError("Fuente de mercado no verificada")
    if analysis.get("action") != "NO_OPERAR":
        raise ValueError("Entrada incompatible con política de solo lectura")
    frames = analysis.get("timeframes")
    if not isinstance(frames, dict) or set(frames) != {"1d", "4h", "1h", "15m"}:
        raise ValueError("Temporalidades incompletas")
    price = Decimal(str(frames["15m"]["close"]))
    if not price.is_finite() or price <= 0:
        raise ValueError("Precio de referencia inválido")
    distance_pct = (order.limit_price / price - Decimal("1")) * Decimal("100")
    downtrend = all(frames[tf]["trend"] == "bajista" for tf in ("4h", "1h", "15m"))
    observations = []
    if downtrend and order.side == "BUY":
        observations.append("Compra pendiente frente a presión bajista en 4H, 1H y 15m; riesgo de continuación.")
    if distance_pct < 0 and order.side == "BUY":
        observations.append("Precio límite de compra por debajo del último cierre de 15m; la ejecución sigue sin verificar.")
    if not observations:
        observations.append("No se identificó un conflicto simple; esto no confirma una oportunidad.")
    return {
        "symbol": order.symbol, "side": order.side, "quantity": str(order.quantity),
        "limit_price": str(order.limit_price), "reference_close_15m": str(price),
        "distance_to_limit_pct": str(round(distance_pct, 4)),
        "nominal_usdt": str(order.quantity * order.limit_price),
        "order_status": "UNVERIFIED", "market_context": analysis["context"],
        "observations": observations, "action": "REVIEW_ONLY",
        "real_orders_enabled": False,
        "limitations": "Orden proporcionada manualmente. No se consultó Binance privado ni se verificó ejecución, saldo o reservas.",
    }

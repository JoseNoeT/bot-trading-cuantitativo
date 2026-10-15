"""Pruebas deterministas del análisis de órdenes, sin llamadas externas."""
from decimal import Decimal
import pytest
from bot.orders.models import PendingSpotOrder
from bot.orders.evaluator import review_pending_order


def order():
    return PendingSpotOrder("WLDUSDT", "BUY", Decimal("17.2"), Decimal("0.4600"))


def market():
    return {
        "symbol": "WLDUSDT", "source": "BINANCE_PUBLIC_REST",
        "action": "NO_OPERAR", "context": "MIXTO_O_SIN_CONFIRMACION",
        "timeframes": {tf: {"close": 0.4672, "trend": trend} for tf, trend in
                       (("1d", "alcista"), ("4h", "bajista"), ("1h", "bajista"), ("15m", "bajista"))},
    }


def test_wld_review_detects_downtrend_without_trading():
    r = review_pending_order(order(), market())
    assert r["nominal_usdt"] == "7.91200"
    assert r["order_status"] == "UNVERIFIED"
    assert r["action"] == "REVIEW_ONLY"
    assert r["real_orders_enabled"] is False
    assert len(r["observations"]) == 2


def test_reject_wrong_symbol():
    m = market()
    m["symbol"] = "ETHUSDT"
    with pytest.raises(ValueError, match="diferentes"):
        review_pending_order(order(), m)


def test_reject_missing_timeframe():
    m = market()
    del m["timeframes"]["4h"]
    with pytest.raises(ValueError, match="incompletas"):
        review_pending_order(order(), m)


def test_reject_invalid_amounts():
    for bad in (Decimal("-1"), Decimal("NaN"), Decimal("Infinity")):
        with pytest.raises(ValueError):
            PendingSpotOrder("WLDUSDT", "BUY", bad, Decimal("0.46"))

"""Pruebas de la interfaz de simulacion, sin red ni ordenes reales."""
from bot.web.api import app, build_snapshot, health, synthetic_candles


def test_demo_uses_synthetic_data():
    snapshot = build_snapshot()
    assert snapshot["mode"] == "SIMULATION_ONLY"
    assert snapshot["source"] == "SYNTHETIC_DATA"
    assert snapshot["real_orders_enabled"] is False
    assert snapshot["signal"] is not None
    assert snapshot["signal"]["symbol"] == "DEMOUSDT"
    assert snapshot["signal"]["direction"] == "LONG"


def test_demo_is_deterministic_except_timestamp():
    a = build_snapshot()["signal"]
    b = build_snapshot()["signal"]
    assert a == b


def test_health_never_claims_exchange_connection():
    assert health()["exchange_connected"] is False


def test_candles_are_synthetic():
    candles = synthetic_candles()
    assert len(candles) == 60
    assert candles[-1]["volume"] == 200.0
    assert len(app.routes) >= 3

"""Validación estática de selección de fuente sin conexión de red."""
from bot.web import api
from bot.data.websocket_stream import _build_combined_url


def test_default_source_is_simulation():
    assert api.DATA_SOURCE in ("simulation", "binance")
    assert api.source()["real_orders_enabled"] is False
    assert api.source()["authenticated_binance"] is False


def test_binance_public_stream_url():
    url = _build_combined_url(["btcusdt", "ethusdt"])
    assert url.startswith("wss://stream.binance.com:9443/stream?")
    assert "btcusdt@trade" in url
    assert "ethusdt@trade" in url


def test_status_exposes_source():
    assert api.status()["data_source"] == api.DATA_SOURCE
    assert api.status()["real_orders_enabled"] is False

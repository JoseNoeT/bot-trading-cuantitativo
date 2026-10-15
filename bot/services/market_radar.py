"""Radar experimental de anomalías usando velas cerradas; no identifica actores."""
from __future__ import annotations
import math
from bot.core.whale_detector import analizar_ballenas
from bot.services.market_intelligence import fetch_closed_candles


def market_radar(symbol: str, *, session=None, now_ms=None) -> dict:
    args = {"interval": "1m", "now_ms": now_ms}
    if session is not None:
        args["session"] = session
    candles = fetch_closed_candles(symbol, **args)
    if len(candles) < 21:
        raise ValueError("Datos insuficientes para radar de volumen")
    event = analizar_ballenas(candles)
    vols = [float(c["volume"]) for c in candles[-21:-1]]
    baseline = sum(vols) / len(vols)
    latest = candles[-1]
    ratio = latest["volume"] / baseline if baseline > 0 else None
    if ratio is not None and not math.isfinite(ratio):
        raise ValueError("Volumen no válido")
    return {
        "symbol": symbol.upper(), "source": "BINANCE_PUBLIC_REST",
        "interval": "1m", "closed_at": latest["timestamp"],
        "volume_relative": round(ratio, 3) if ratio is not None else None,
        "flags": {key: bool(event[key]) for key in ("volume_spike", "fast_move", "stop_hunt", "squeeze")},
        "level": event["severity"],
        "observations": event["razones"],
        "whale_confirmed": False,
        "limitations": "Anomalías de velas; no identifica ballenas ni manipulación. No usa order book ni flujo de órdenes.",
        "action": "OBSERVAR", "real_orders_enabled": False,
    }

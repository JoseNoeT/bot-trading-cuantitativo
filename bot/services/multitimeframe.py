"""Top-down context, strictly read-only. No actionable order or calibrated probability."""
from __future__ import annotations

from typing import Any
import requests

from bot.core.indicators import ema, rsi, atr
from bot.core.strategy import detectar_tendencia
from bot.services.market_intelligence import fetch_closed_candles

TIMEFRAMES = ("1d", "4h", "1h", "15m")


def analyze_multitimeframe(symbol: str, *, session: Any = requests, now_ms: int | None = None) -> dict:
    results = {}
    for interval in TIMEFRAMES:
        candles = fetch_closed_candles(symbol, session=session, now_ms=now_ms, interval=interval)
        closes = [v["close"] for v in candles]
        item = {
            "interval": interval,
            "trend": detectar_tendencia(candles),
            "close": closes[-1],
            "close_time": candles[-1]["timestamp"],
            "ema20": round(ema(closes, 20), 8),
            "ema50": round(ema(closes, 50), 8),
            "rsi14": round(rsi(closes, 14), 4),
            "atr14": round(atr([v["high"] for v in candles], [v["low"] for v in candles], closes, 14), 8),
            "candles": len(candles),
        }
        results[interval] = item
    major = [results[tf]["trend"] for tf in ("1d", "4h")]
    medium = results["1h"]["trend"]
    trigger = results["15m"]["trend"]
    if major == ["alcista", "alcista"] and medium == "alcista" and trigger == "alcista":
        context = "ALCISTA_ALINEADO"
        explanation = "Tendencias alineadas; falta validar setup, costos, riesgo y ejecución."
    elif major == ["bajista", "bajista"]:
        context = "BAJISTA_DOMINANTE"
        explanation = "Tendencia bajista en 1D y 4H: un rebote de 15m no confirma reversión."
    else:
        context = "MIXTO_O_SIN_CONFIRMACION"
        explanation = "Temporalidades sin alineación suficiente. Esperar confirmaciones."
    return {
        "symbol": symbol.upper(), "source": "BINANCE_PUBLIC_REST", "timeframes": results,
        "context": context, "explanation": explanation,
        "action": "NO_OPERAR", "risk_status": "NOT_VERIFIED",
        "real_orders_enabled": False, "confidence_type": "NO_PROBABILISTIC_CONFIDENCE",
    }

"""Read-only market intelligence from Binance public closed candles.

This module never accesses account balances or sends orders.
"""
from __future__ import annotations

import math
import time
from datetime import datetime, timezone
from typing import Any

import requests

from bot.core import indicators
from bot.core.strategy import detectar_tendencia, generar_pre_senal

ALLOWED = frozenset({"BTCUSDT", "ETHUSDT", "WLDUSDT"})
INTERVAL = "1m"
LIMIT = 100
INTERVAL_MS = {"1m": 60_000, "15m": 900_000, "1h": 3_600_000, "4h": 14_400_000, "1d": 86_400_000}
URL = "https://api.binance.com/api/v3/klines"


def fetch_closed_candles(symbol: str, *, session: Any = requests, now_ms: int | None = None, interval: str = INTERVAL) -> list[dict]:
    symbol = symbol.upper()
    if interval not in INTERVAL_MS:
        raise ValueError("Temporalidad no permitida")
    if symbol not in ALLOWED:
        raise ValueError("Símbolo no permitido")
    response = session.get(URL, params={"symbol": symbol, "interval": interval, "limit": LIMIT}, timeout=8)
    response.raise_for_status()
    rows = response.json()
    if not isinstance(rows, list):
        raise ValueError("Respuesta Binance inválida")
    now = int(time.time() * 1000) if now_ms is None else now_ms
    candles = []
    previous = -1
    for row in rows:
        if not isinstance(row, list) or len(row) < 7:
            raise ValueError("Vela incompleta")
        opened, closed = int(row[0]), int(row[6])
        if opened <= previous:
            raise ValueError("Velas desordenadas o duplicadas")
        previous = opened
        if closed >= now:
            continue  # Jamás calcular una señal usando una vela abierta.
        op, hi, lo, price, vol = (float(row[i]) for i in (1, 2, 3, 4, 5))
        if not all(math.isfinite(v) for v in (op, hi, lo, price, vol)):
            raise ValueError("Datos no finitos")
        if min(op, hi, lo, price) <= 0 or vol < 0 or lo > min(op, price) or hi < max(op, price):
            raise ValueError("OHLC inválido")
        candles.append({"timestamp": closed // 1000, "open": op, "high": hi,
                        "low": lo, "close": price, "volume": vol})
    if len(candles) < 60:
        raise ValueError("Datos históricos insuficientes")
    if now - candles[-1]["timestamp"] * 1000 > INTERVAL_MS[interval] * 3:
        raise ValueError("Datos de mercado desactualizados")
    return candles


def analyze(symbol: str, *, session: Any = requests, now_ms: int | None = None) -> dict:
    """Analysis only. A setup is NOT an executable order or probability."""
    symbol = symbol.upper()
    candles = fetch_closed_candles(symbol, session=session, now_ms=now_ms)
    closes = [c["close"] for c in candles]
    latest = candles[-1]
    ema20 = indicators.ema(closes, 20)
    ema50 = indicators.ema(closes, 50)
    atr14 = indicators.atr([c["high"] for c in candles], [c["low"] for c in candles], closes, 14)
    trend = detectar_tendencia(candles)
    setup = generar_pre_senal(candles)
    status = "SETUP_DETECTED" if setup else "WAIT"
    return {
        "symbol": symbol, "source": "BINANCE_PUBLIC_REST", "interval": INTERVAL,
        "closed_candles": len(candles), "last_close_time": latest["timestamp"],
        "evaluated_at": datetime.now(timezone.utc).isoformat(),
        "last_close": latest["close"], "ema20": round(ema20, 8),
        "ema50": round(ema50, 8), "rsi14": round(indicators.rsi(closes, 14), 4),
        "atr14": round(atr14, 8), "trend": trend,
        "status": status, "direction": setup["direction"] if setup else None,
        "reason": setup["reason"] if setup else ["Sin configuración completa para señal"],
        "risk_status": "NOT_VERIFIED",
        "action": "NO_OPERAR",
        "real_orders_enabled": False,
        "note": "Pre-señal informativa. No se validó saldo, exposición, pérdidas ni autorización.",
    }

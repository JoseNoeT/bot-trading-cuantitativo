"""Evaluador conservador de configuraciones Spot basado en evidencia multitemporal.

No genera órdenes, tamaños, SL/TP ni probabilidades. Nunca interpreta SHORT
como permiso de abrir una posición Spot en corto.
"""
from __future__ import annotations

from typing import Any

TIMEFRAMES = ("1d", "4h", "1h", "15m")


def evaluate_spot_opportunity(market: dict[str, Any], radar: dict[str, Any] | None = None) -> dict[str, Any]:
    if market.get("symbol") != "WLDUSDT" or market.get("source") != "BINANCE_PUBLIC_REST":
        raise ValueError("Se requieren datos públicos verificados de WLDUSDT")
    frames = market.get("timeframes")
    if not isinstance(frames, dict) or any(tf not in frames for tf in TIMEFRAMES):
        raise ValueError("Temporalidades incompletas")
    trends = {}
    for tf in TIMEFRAMES:
        frame = frames[tf]
        trend = frame.get("trend")
        if trend not in {"alcista", "bajista", "neutral"}:
            raise ValueError("Tendencia inválida")
        trends[tf] = trend
    reasons = []
    if trends["1d"] == trends["4h"] == trends["1h"] == trends["15m"] == "alcista":
        state = "OBSERVAR_CONFIGURACION_ALCISTA"
        reasons.append("Las cuatro temporalidades muestran tendencia alcista.")
    elif trends["4h"] == trends["1h"] == trends["15m"] == "bajista":
        state = "EVITAR_COMPRAS_IMPULSIVAS"
        reasons.append("4H, 1H y 15m bajistas: riesgo de continuar la caída.")
    else:
        state = "SIN_CONFIRMACION"
        reasons.append("Las temporalidades no ofrecen alineación suficiente.")
    if radar is None:
        reasons.append("Radar de actividad no consultado.")
    else:
        if radar.get("symbol") != "WLDUSDT" or radar.get("source") != "BINANCE_PUBLIC_REST":
            raise ValueError("Radar no corresponde al activo o fuente")
        if radar.get("whale_confirmed") is not False:
            raise ValueError("El radar no puede certificar ballenas")
        reasons.append("Radar experimental: actividad anómala no constituye señal de compra.")
    return {
        "symbol": "WLDUSDT", "state": state, "timeframes": trends,
        "reasons": reasons, "action": "NO_OPERAR", "execution_enabled": False,
        "risk_status": "NOT_VERIFIED", "evidence": "HEURISTIC_NOT_BACKTESTED",
        "note": "Falta validar entradas, salidas, comisiones, slippage y riesgo mediante simulación.",
    }

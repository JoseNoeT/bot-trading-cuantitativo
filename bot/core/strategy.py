"""
strategy.py
Lógica principal de la estrategia del bot.
Referencias: docs/03_Modulos_Core.md y docs/04_Estrategia_Base.md
"""
 
from __future__ import annotations

import math
from typing import Dict, List, Optional

from bot.core import indicators


def _extract_series(candles: List[Dict], key: str) -> List[float]:
    return [float(c.get(key, 0.0)) for c in candles]


def detectar_tendencia(candles: List[Dict]) -> str:
    """Detecta la tendencia del mercado usando EMA20 y EMA50.

    Reglas:
    - Calcula EMA20 y EMA50 sobre los cierres.
    - Si EMA20 > EMA50 => 'alcista'
    - Si EMA20 < EMA50 => 'bajista'
    - Si están muy juntas o cruzándose => 'neutral'

    Retorna: 'alcista' | 'bajista' | 'neutral'

    No lanza excepciones en condiciones normales; si hay pocos datos
    devuelve 'neutral'.
    """
    closes = _extract_series(candles, "close")
    if len(closes) < 50:
        return "neutral"

    try:
        ema20 = indicators.ema(closes, 20)
        ema50 = indicators.ema(closes, 50)
    except Exception:
        # En caso de error numérico, devolver neutral y dejar que
        # el risk manager o caller decida.
        return "neutral"

    # Si están muy próximas (ej. diferencia relativa < 0.15%), consideramos neutral
    if ema50 == 0:
        return "neutral"

    rel_diff = abs(ema20 - ema50) / ema50
    if rel_diff < 0.0015:
        return "neutral"

    # Detectar cruces recientes: comparar EMA20 respecto a EMA50 en el punto anterior
    # para evitar señales cuando están cruzándose.
    try:
        ema20_prev = indicators.ema(closes[:-1], 20)
        ema50_prev = indicators.ema(closes[:-1], 50)
        crossing = (ema20_prev - ema50_prev) * (ema20 - ema50) < 0
        if crossing:
            return "neutral"
    except Exception:
        # Ignorar y continuar si no puede calcular previas
        pass

    return "alcista" if ema20 > ema50 else "bajista"


def validar_volumen(candles: List[Dict], factor: float = 1.5, window: int = 20) -> bool:
    """Valida si el volumen de la última vela supera el promedio de la ventana por un factor.

    Args:
        candles: lista de velas con key 'volume'.
        factor: umbral multiplicador sobre el promedio.
        window: tamaño de la ventana para calcular el promedio.

    Returns:
        True si volumen_actual > promedio * factor, False en caso contrario.

    Si hay datos insuficientes devuelve False.
    """
    vols = _extract_series(candles, "volume")
    if len(vols) < 2:
        return False

    w = min(window, len(vols))
    avg_vol = sum(vols[-w:]) / w
    last_vol = vols[-1]
    if avg_vol <= 0:
        return False
    return last_vol > avg_vol * float(factor)


def validar_volatilidad(candles: List[Dict], length: int = 14) -> float:
    """Calcula el ATR para la serie de velas proporcionada.

    Devuelve un float con el ATR calculado usando `indicators.atr`.
    Si hay errores o datos insuficientes devuelve math.nan.
    """
    highs = _extract_series(candles, "high")
    lows = _extract_series(candles, "low")
    closes = _extract_series(candles, "close")
    try:
        atr_val = indicators.atr(highs, lows, closes, length)
        return float(atr_val)
    except Exception:
        return math.nan


def generar_pre_senal(candles: List[Dict]) -> Optional[Dict]:
    """Genera una pre-señal basada en Tendencia + Volumen + ATR + condiciones sencillas.

    Reglas principales:
    - No operar si len(candles) < 50
    - No operar si tendencia == 'neutral'
    - Validar volumen con `validar_volumen`
    - Para LONG: tendencia 'alcista' y cierre último > EMA20 y volumen válido
    - Para SHORT: tendencia 'bajista' y cierre último < EMA20 y volumen válido

    Retorna un dict con keys: direction, entry_price, atr, timestamp, reason
    o None si no hay setup válido.
    """
    if not candles or len(candles) < 50:
        return None

    closes = _extract_series(candles, "close")
    last = candles[-1]
    last_close = float(last.get("close", 0.0))
    timestamp = int(last.get("timestamp", 0))

    tendencia = detectar_tendencia(candles)
    if tendencia == "neutral":
        return None

    # calcular EMAs para decisiones
    try:
        ema20 = indicators.ema(closes, 20)
        ema50 = indicators.ema(closes, 50)
    except Exception:
        return None

    volumen_ok = validar_volumen(candles)
    atr_val = validar_volatilidad(candles)

    reasons: List[str] = []
    reasons.append(f"tendencia {tendencia}")

    if volumen_ok:
        # incluir factor aproximado de volumen
        vols = _extract_series(candles, "volume")
        avg_vol = sum(vols[-20:]) / min(20, len(vols))
        factor = vols[-1] / avg_vol if avg_vol > 0 else 0.0
        reasons.append(f"volumen x{factor:.2f}")
    else:
        reasons.append("volumen insuficiente")

    reasons.append("EMA20/EMA50 alineadas" if abs(ema20 - ema50) / (abs(ema50) + 1e-9) < 0.01 else "EMA20/EMA50 separadas")

    # Setup LONG
    if tendencia == "alcista" and last_close > ema20 and volumen_ok:
        return {
            "direction": "LONG",
            "entry_price": float(last_close),
            "atr": float(atr_val) if not math.isnan(atr_val) else None,
            "timestamp": timestamp,
            "reason": reasons,
        }

    # Setup SHORT
    if tendencia == "bajista" and last_close < ema20 and volumen_ok:
        return {
            "direction": "SHORT",
            "entry_price": float(last_close),
            "atr": float(atr_val) if not math.isnan(atr_val) else None,
            "timestamp": timestamp,
            "reason": reasons,
        }

    return None


__all__ = ["detectar_tendencia", "validar_volumen", "validar_volatilidad", "generar_pre_senal"]


"""
whale_detector.py

Detección de actividad de ballenas y manipulación de mercado a partir
de velas recientes. Funciones puras, sin dependencias externas, diseñadas
para integrarse con `signal_engine.py`.

Salida estructurada esperada por `signal_engine`: dict con flags booleanos,
`severity` y `razones` (lista de strings legibles).
"""

from __future__ import annotations

from typing import Dict, List


def _safe_last(candles: List[Dict], idx: int = -1) -> Dict:
    if not candles:
        return {}
    try:
        return dict(candles[idx])
    except Exception:
        return dict(candles[-1])


def detectar_volumen_extremo(candles: List[Dict], factor: float = 2.0, window: int = 20) -> bool:
    """Detecta un spike de volumen contra el promedio de las últimas N velas.

    - Si hay menos de `window` velas devuelve False.
    - No modifica `candles`.
    """
    if not candles or len(candles) < window:
        return False
    vols = []
    # use last `window` volumes
    for c in candles[-window:]:
        v = c.get("volume")
        try:
            vols.append(float(v))
        except Exception:
            vols.append(0.0)
    if not vols:
        return False
    avg = sum(vols) / len(vols)
    # current volume = last candle volume
    last_v = candles[-1].get("volume")
    try:
        last_v = float(last_v)
    except Exception:
        return False
    return last_v > (avg * factor)


def detectar_fast_move(candles: List[Dict], threshold_pct: float = 0.01) -> bool:
    """Detecta movimientos rápidos comparando el último cierre con el anterior.

    - threshold_pct: por ejemplo 0.01 = 1%
    - Devuelve False si no hay suficientes velas.
    """
    if not candles or len(candles) < 2:
        return False
    last = candles[-1]
    prev = candles[-2]
    try:
        close_last = float(last.get("close", 0.0))
        close_prev = float(prev.get("close", 0.0))
    except Exception:
        return False
    if close_prev == 0:
        return False
    delta = close_last - close_prev
    return abs(delta / close_prev) > abs(threshold_pct)


def detectar_stop_hunt(candles: List[Dict], factor: float = 1.5) -> bool:
    """Detecta mechas largas (colas) en la última vela que sugieran stop-hunt.

    - Calcula wick superior/inferior usando `close` como referencia según la especificación.
    - Devuelve False si no hay velas.
    """
    if not candles:
        return False
    last = _safe_last(candles)
    try:
        high = float(last.get("high", 0.0))
        low = float(last.get("low", 0.0))
        close = float(last.get("close", 0.0))
    except Exception:
        return False
    candle_range = high - low
    if candle_range <= 0:
        return False
    upper_wick = high - close
    lower_wick = close - low
    # consider either wick large enough
    threshold = candle_range * factor * 0.5
    return (upper_wick > threshold) or (lower_wick > threshold)


def detectar_squeeze(candles: List[Dict], window: int = 30) -> bool:
    """Detecta compresión de volatilidad seguida de expansión (squeeze).

    Implementación pragmática:
    - Requiere al menos `window + 1` velas (ventana histórica + vela de expansión).
    - Calcula el rango promedio de la ventana histórica (las `window` velas previas a la última).
    - Comprime si el promedio histórico es pequeño (umbral absoluto razonable).
    - Expande si el último rango supera `1.5 * avg_hist`.
    - Devuelve True si hay compresión + expansión.
    """
    if not candles or len(candles) < (window + 1):
        return False
    # compute hist ranges using the `window` candles immediately before the last candle
    start = - (window + 1)
    hist_slice = candles[start:-1]
    ranges_hist = []
    for c in hist_slice:
        try:
            ranges_hist.append(float(c.get("high", 0.0)) - float(c.get("low", 0.0)))
        except Exception:
            ranges_hist.append(0.0)
    if not ranges_hist:
        return False
    avg_hist = sum(ranges_hist) / len(ranges_hist)
    # last range
    last = _safe_last(candles)
    try:
        last_range = float(last.get("high", 0.0)) - float(last.get("low", 0.0))
    except Exception:
        return False

    # Compressed: average historic range is relatively small in absolute terms
    compressed = avg_hist < 1.0
    # Expanded: last range is significantly larger than historic average
    expanded = avg_hist > 0 and last_range > (avg_hist * 1.5)
    return compressed and expanded


def detectar_whale_trade(candles: List[Dict], trade_factor: float = 3.0, window: int = 20) -> bool:
    """Detecta posibles órdenes grandes usando el cuerpo de la vela como proxy.

    - body = abs(close - open)
    - compara el cuerpo de la última vela contra el promedio de cuerpos en la ventana
    - requiere al menos `window` velas
    """
    if not candles or len(candles) < window:
        return False
    bodies = []
    for c in candles[-window:]:
        try:
            bodies.append(abs(float(c.get("close", 0.0)) - float(c.get("open", 0.0))))
        except Exception:
            bodies.append(0.0)
    if not bodies:
        return False
    avg = sum(bodies) / len(bodies)
    last_body = bodies[-1]
    return last_body > (avg * trade_factor)


def clasificar_severidad(eventos: Dict[str, bool]) -> str:
    """Clasifica severidad en 'low', 'medium', 'high' según número de flags True.

    - 3 o más -> 'high'
    - 2 -> 'medium'
    - 1 -> 'low'
    - 0 -> 'low'
    """
    if not eventos:
        return "low"
    count = sum(1 for v in eventos.values() if bool(v))
    if count >= 3:
        return "high"
    if count == 2:
        return "medium"
    return "low"


def analizar_ballenas(candles: List[Dict]) -> Dict:
    """Analiza velas y devuelve dict estructurado con flags, severity y razones.

    Output example:
    {
        "volume_spike": True/False,
        "whale_trade": True/False,
        "fast_move": True/False,
        "stop_hunt": True/False,
        "squeeze": True/False,
        "severity": "low"|"medium"|"high",
        "razones": [ ... ]
    }
    """
    # Non-destructive: do not mutate `candles`
    eventos: Dict[str, bool] = {}
    eventos["volume_spike"] = detectar_volumen_extremo(candles)
    eventos["whale_trade"] = detectar_whale_trade(candles)
    eventos["fast_move"] = detectar_fast_move(candles)
    eventos["stop_hunt"] = detectar_stop_hunt(candles)
    eventos["squeeze"] = detectar_squeeze(candles)

    severity = clasificar_severidad({
        k: eventos[k] for k in ("volume_spike", "whale_trade", "fast_move", "stop_hunt", "squeeze")
    })

    razones: List[str] = []
    if eventos.get("volume_spike"):
        razones.append("Volumen extremo detectado")
    if eventos.get("whale_trade"):
        razones.append("Cuerpo de vela anómalo / orden grande")
    if eventos.get("fast_move"):
        razones.append("Movimiento rápido de precio")
    if eventos.get("stop_hunt"):
        razones.append("Mecha larga detectada (stop hunt)")
    if eventos.get("squeeze"):
        razones.append("Compresión + expansión detectada (squeeze)")

    out = dict(eventos)
    out["severity"] = severity
    out["razones"] = razones
    return out


__all__ = [
    "detectar_volumen_extremo",
    "detectar_fast_move",
    "detectar_stop_hunt",
    "detectar_squeeze",
    "detectar_whale_trade",
    "clasificar_severidad",
    "analizar_ballenas",
]
"""
whale_detector.py
Radar de ballenas y detección de volumen anómalo.
Referencias: docs/06_Radar_de_Ballenas.md
"""

def placeholder():
    """Placeholder para detection functions.

    Implementar detectores en FASE 3.
    """
    return None

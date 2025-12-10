"""
indicators.py
Módulo de indicadores técnicos para el bot de trading cuantitativo.

Este archivo implementa funciones puras y numéricamente estables para:
- SMA, EMA
- ATR
- RSI (Wilder smoothing)
- MACD (línea MACD, línea señal, histograma)
- Volatility (desviación estándar de cambios de precio)

Reglas:
- No se usan librerías externas (solo `math`).
- Validación de inputs y errores claros cuando la longitud es insuficiente.
- Funciones puras: no modifican las listas de entrada.

Referencias: docs/03_Modulos_Core.md, docs/04_Estrategia_Base.md
"""

from __future__ import annotations

import math
from typing import List, Tuple


def _mean(values: List[float]) -> float:
    return sum(values) / len(values)


def sma(values: List[float], length: int) -> float:
    """Simple Moving Average (SMA).

    Args:
        values: serie de precios (ordenada cronológicamente, más antigua -> más reciente).
        length: ventana para el promedio.

    Returns:
        Último valor de la SMA calculada sobre la ventana final.

    Raises:
        ValueError: si la longitud de `values` es menor que `length` o si `length` <= 0.
    """
    if length <= 0:
        raise ValueError("length must be > 0")
    if len(values) < length:
        raise ValueError(f"Not enough data points for SMA: need {length}, got {len(values)}")

    window = values[-length:]
    return _mean(window)


def ema(values: List[float], length: int) -> float:
    """Exponential Moving Average (EMA).

    Implementación clásica: la EMA se inicializa con la SMA de la primera ventana
    y luego se aplica la fórmula recursiva con el multiplicador alpha = 2/(length+1).

    Args:
        values: serie de precios (cronológica).
        length: periodo de la EMA.

    Returns:
        Valor final de la EMA.

    Raises:
        ValueError: si hay datos insuficientes o periodo inválido.
    """
    if length <= 0:
        raise ValueError("length must be > 0")
    n = len(values)
    if n < length:
        raise ValueError(f"Not enough data points for EMA: need {length}, got {n}")

    alpha = 2.0 / (length + 1)

    # Inicializar con SMA sobre los primeros `length` valores
    ema_prev = _mean(values[:length])

    # Iterar desde index `length` hasta el final
    for price in values[length:]:
        ema_prev = (price - ema_prev) * alpha + ema_prev

    return ema_prev


def atr(high: List[float], low: List[float], close: List[float], length: int) -> float:
    """Average True Range (ATR).

    Calcula el TR por vela y devuelve la media simple de las últimas `length` TRs.

    Args:
        high, low, close: listas de la misma longitud con OHLC (cronológico).
        length: ventana para el ATR.

    Returns:
        Valor del ATR (en las mismas unidades de precio).

    Raises:
        ValueError: si las listas no tienen igual longitud o hay pocos datos.
    """
    if length <= 0:
        raise ValueError("length must be > 0")
    if not (len(high) == len(low) == len(close)):
        raise ValueError("high, low and close must have the same length")
    n = len(close)
    if n < 2:
        raise ValueError("At least two candles are required to compute ATR")

    # Calcular True Range (TR) para cada vela (desde i=1)
    tr_values: List[float] = []
    for i in range(1, n):
        high_low = high[i] - low[i]
        high_prev_close = abs(high[i] - close[i - 1])
        low_prev_close = abs(low[i] - close[i - 1])
        tr = max(high_low, high_prev_close, low_prev_close)
        tr_values.append(tr)

    if len(tr_values) < length:
        raise ValueError(f"Not enough TR values for ATR: need {length}, got {len(tr_values)}")

    window = tr_values[-length:]
    return _mean(window)


def rsi(values: List[float], length: int = 14) -> float:
    """Relative Strength Index (RSI) usando suavizado de Wilder.

    Implementación:
    - Se calculan las diferencias entre cierres consecutivos.
    - Se inicializan avg_gain y avg_loss con la media de las primeras `length` diferencias.
    - Se aplica el suavizado Wilder para el resto de la serie.

    Args:
        values: serie de precios (cronológica).
        length: periodo del RSI (por defecto 14).

    Returns:
        RSI en rango [0, 100].

    Raises:
        ValueError: si hay datos insuficientes o parámetros inválidos.
    """
    if length <= 0:
        raise ValueError("length must be > 0")
    n = len(values)
    if n < length + 1:
        raise ValueError(f"Not enough data points for RSI: need {length+1}, got {n}")

    # Calcular cambios día a día
    deltas: List[float] = [values[i] - values[i - 1] for i in range(1, n)]

    gains = [d for d in deltas[:length] if d > 0]
    losses = [-d for d in deltas[:length] if d < 0]

    avg_gain = sum(gains) / length if gains else 0.0
    avg_loss = sum(losses) / length if losses else 0.0

    # Aplicar suavizado de Wilder
    for d in deltas[length:]:
        gain = d if d > 0 else 0.0
        loss = -d if d < 0 else 0.0
        avg_gain = (avg_gain * (length - 1) + gain) / length
        avg_loss = (avg_loss * (length - 1) + loss) / length

    if avg_loss == 0.0:
        return 100.0 if avg_gain > 0 else 50.0

    rs = avg_gain / avg_loss
    rsi_value = 100.0 - (100.0 / (1.0 + rs))
    return rsi_value


def _ema_series(values: List[float], length: int) -> List[float]:
    """Helper: devuelve la serie completa de EMA (alineada con `values`).

    La serie comienza a partir del índice `length-1` (primer EMA calculable).
    """
    if length <= 0:
        raise ValueError("length must be > 0")
    n = len(values)
    if n < length:
        raise ValueError(f"Not enough data points for EMA series: need {length}, got {n}")

    alpha = 2.0 / (length + 1)
    ema_vals: List[float] = []
    ema_prev = _mean(values[:length])
    ema_vals.append(ema_prev)

    for price in values[length:]:
        ema_prev = (price - ema_prev) * alpha + ema_prev
        ema_vals.append(ema_prev)

    return ema_vals


def macd(values: List[float], fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[float, float, float]:
    """Calcula MACD Line, Signal Line y Histogram.

    Strategy:
    - Calcula la serie EMA rápida y lenta.
    - Construye la serie MACD como diferencia punto a punto entre EMAs (donde ambas existen).
    - Calcula la EMA de la serie MACD con periodo `signal` y devuelve los últimos valores.

    Args:
        values: serie de precios (cronológica).
        fast: periodo EMA rápido (por defecto 12).
        slow: periodo EMA lento (por defecto 26).
        signal: periodo para la línea señal (por defecto 9).

    Returns:
        (macd_line, signal_line, histogram)

    Raises:
        ValueError: si las longitudes son inválidas o datos insuficientes.
    """
    if not (0 < fast < slow):
        raise ValueError("Require 0 < fast < slow for MACD")
    n = len(values)
    if n < slow + signal:
        raise ValueError(f"Not enough data points for MACD: need at least {slow+signal}, got {n}")

    # Series de EMA completas (cada una empieza en su índice correspondiente)
    ema_fast_series = _ema_series(values, fast)
    ema_slow_series = _ema_series(values, slow)

    # Alinear las series: ema_slow_series empieza más tarde que ema_fast_series.
    # Para cada punto utilizable tomar la diferencia donde ambas existen.
    # ema_fast_series corresponds to values[fast-1:], ema_slow_series to values[slow-1:]
    offset_fast = fast - 1
    offset_slow = slow - 1

    macd_series: List[float] = []
    # Iterar sobre indices donde ambas EMAs existen
    for i in range(offset_slow, n):
        idx_fast = i - offset_fast
        idx_slow = i - offset_slow
        macd_val = ema_fast_series[idx_fast] - ema_slow_series[idx_slow]
        macd_series.append(macd_val)

    # Señal: EMA de la serie MACD
    if len(macd_series) < signal:
        raise ValueError("Not enough MACD points to compute signal line")

    # Calcular EMA sobre macd_series y devolver último valor
    signal_ema = _ema_series(macd_series, signal)[-1]
    macd_line = macd_series[-1]
    histogram = macd_line - signal_ema
    return macd_line, signal_ema, histogram


def volatility(values: List[float], length: int = 20) -> float:
    """Devuelve la desviación estándar de los cambios de precio (última `length` observaciones).

    Se usan cambios relativos simples: (p_t - p_{t-1}) / p_{t-1}.

    Args:
        values: serie de precios (cronológica).
        length: ventana para el cálculo.

    Returns:
        Desviación estándar (en unidades de retorno, no en puntos de precio).

    Raises:
        ValueError: si hay datos insuficientes o parámetros inválidos.
    """
    if length <= 0:
        raise ValueError("length must be > 0")
    n = len(values)
    if n < length + 1:
        raise ValueError(f"Not enough data points for volatility: need {length+1}, got {n}")

    # Calcular retornos simples
    returns: List[float] = []
    for i in range(1, n):
        prev = values[i - 1]
        if prev == 0:
            returns.append(0.0)
        else:
            returns.append((values[i] - prev) / prev)

    window = returns[-length:]
    mean_r = _mean(window)
    var = sum((r - mean_r) ** 2 for r in window) / len(window)
    return math.sqrt(var)


__all__ = ["sma", "ema", "atr", "rsi", "macd", "volatility"]


"""
Tests unitarios para indicators.py
FASE 2 — Núcleo Cuantitativo
Autor: José Miguel Noé Torres
"""

import math
import pytest

from bot.core import indicators as ind


def test_sma_simple():
    values = [1, 2, 3, 4, 5]
    assert ind.sma(values, 3) == pytest.approx(4.0)


def test_sma_errors():
    with pytest.raises(ValueError):
        ind.sma([], 3)
    with pytest.raises(ValueError):
        ind.sma([1, 2], 3)
    with pytest.raises(ValueError):
        ind.sma([1, 2, 3], 0)


def test_ema_known_simple():
    # Caso sencillo: length=2, values=[1,2,3]
    # alpha = 2/(2+1) = 2/3
    # SMA(initial) = (1+2)/2 = 1.5
    # EMA_next = (3 - 1.5) * 2/3 + 1.5 = 2.5
    assert ind.ema([1, 2, 3], 2) == pytest.approx(2.5)


def test_ema_errors():
    with pytest.raises(ValueError):
        ind.ema([], 3)
    with pytest.raises(ValueError):
        ind.ema([1, 2], 3)
    with pytest.raises(ValueError):
        ind.ema([1, 2, 3], 0)


def test_atr_basic():
    high = [10, 11, 12]
    low = [9, 10, 10]
    close = [9, 10, 11]
    # TRs: [2,2] -> ATR with length=2 equals 2.0
    assert ind.atr(high, low, close, 2) == pytest.approx(2.0)


def test_atr_errors():
    with pytest.raises(ValueError):
        ind.atr([], [], [], 2)
    with pytest.raises(ValueError):
        ind.atr([1, 2], [1], [1, 2], 2)
    with pytest.raises(ValueError):
        ind.atr([1, 2], [1, 2], [1, 2], 0)


def test_rsi_basic():
    # Construir una serie con suficiente longitud (>= length+1)
    values = [1.0 + 0.5 * math.sin(i) for i in range(30)]
    r = ind.rsi(values, length=14)
    assert isinstance(r, float)
    assert 0.0 <= r <= 100.0


def test_rsi_errors():
    with pytest.raises(ValueError):
        ind.rsi([], 14)
    with pytest.raises(ValueError):
        ind.rsi([1, 2, 3], 5)  # insufficient for length+1


def test_macd_basic():
    # Usar una secuencia lineal para comprobar que MACD devuelve floats
    values = list(range(1, 41))  # 1..40
    macd_line, signal_line, histogram = ind.macd(values, fast=12, slow=26, signal=9)
    assert isinstance(macd_line, float)
    assert isinstance(signal_line, float)
    assert isinstance(histogram, float)


def test_macd_errors():
    with pytest.raises(ValueError):
        ind.macd([1, 2, 3], fast=12, slow=26, signal=9)
    with pytest.raises(ValueError):
        ind.macd(list(range(30)), fast=26, slow=12, signal=9)  # invalid fast/slow


def test_volatility_basic():
    # Serie con pequeñas variaciones alrededor de 100
    values = [100.0, 100.5, 101.0, 100.8, 101.2, 101.0, 100.9, 101.1, 101.05, 101.2, 101.15]
    v = ind.volatility(values, length=5)
    assert isinstance(v, float)
    assert v >= 0.0
    # Para este tipo de series la volatilidad debe ser pequeña
    assert v < 0.02


def test_volatility_errors():
    with pytest.raises(ValueError):
        ind.volatility([], 5)
    with pytest.raises(ValueError):
        ind.volatility([100.0, 101.0], 5)

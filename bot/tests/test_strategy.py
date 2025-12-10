"""
Tests unitarios para strategy.py
FASE 3 — Estrategia Base Cuantitativa
Autor: José Miguel Noé Torres
"""

import pytest
import math

from bot.core.strategy import (
    detectar_tendencia,
    validar_volumen,
    validar_volatilidad,
    generar_pre_senal,
)


def make_candle(close, volume, ts):
    return {"open": close, "high": close, "low": close, "close": close, "volume": volume, "timestamp": ts}


def test_tendencia_alcista():
    candles = [
        {"close": float(p), "open": float(p - 1), "high": float(p), "low": float(p - 1), "volume": 100.0, "timestamp": i}
        for i, p in enumerate(range(1, 60))
    ]
    assert detectar_tendencia(candles) == "alcista"


def test_tendencia_bajista():
    candles = [
        {"close": float(p), "open": float(p + 1), "high": float(p + 1), "low": float(p), "volume": 100.0, "timestamp": i}
        for i, p in enumerate(range(60, 0, -1))
    ]
    assert detectar_tendencia(candles) == "bajista"


def test_tendencia_neutral():
    candles = [
        {"close": 100.0, "open": 100.0, "high": 100.0, "low": 100.0, "volume": 100.0, "timestamp": i}
        for i in range(60)
    ]
    assert detectar_tendencia(candles) == "neutral"


def test_validar_volumen_positivo():
    candles = [make_candle(1.0, 10.0, i) for i in range(20)]
    candles.append(make_candle(1.0, 40.0, 21))
    assert validar_volumen(candles, factor=2.0) is True


def test_validar_volumen_negativo():
    candles = [make_candle(1.0, 10.0, i) for i in range(20)]
    candles.append(make_candle(1.0, 11.0, 21))
    assert validar_volumen(candles, factor=2.0) is False


def test_validar_volatilidad_atr():
    # Serie con movimiento para ATR
    candles = []
    for i, p in enumerate(range(100, 160)):
        candles.append({
            "open": float(p - 1),
            "high": float(p + 1),
            "low": float(p - 2),
            "close": float(p),
            "volume": 50.0,
            "timestamp": i,
        })
    atr_value = validar_volatilidad(candles)
    assert isinstance(atr_value, float)
    assert atr_value > 0


def test_pre_senal_long_valida():
    candles = []
    for i, p in enumerate(range(1, 60)):
        candles.append({
            "open": float(p - 1),
            "high": float(p),
            "low": float(p - 1),
            "close": float(p),
            "volume": 20.0,
            "timestamp": i,
        })

    # volumen fuerte en la última vela
    candles[-1]["volume"] = 200.0

    signal = generar_pre_senal(candles)
    assert signal is not None
    assert signal["direction"] == "LONG"


def test_pre_senal_short_valida():
    candles = []
    for i, p in enumerate(range(100, 40, -1)):
        candles.append({
            "open": float(p + 1),
            "high": float(p + 1),
            "low": float(p),
            "close": float(p),
            "volume": 20.0,
            "timestamp": i,
        })

    candles[-1]["volume"] = 200.0

    signal = generar_pre_senal(candles)
    assert signal is not None
    assert signal["direction"] == "SHORT"


def test_rechazo_por_tendencia_neutral():
    candles = [make_candle(100.0, 200.0, i) for i in range(60)]
    # Incluso con volumen alto, debe ser neutral y no generar señal
    signal = generar_pre_senal(candles)
    assert signal is None


def test_rechazo_por_volumen_insuficiente():
    candles = []
    for i, p in enumerate(range(1, 60)):
        candles.append({
            "open": float(p - 1),
            "high": float(p),
            "low": float(p - 1),
            "close": float(p),
            "volume": 1.0,  # volumen muy bajo
            "timestamp": i,
        })
    signal = generar_pre_senal(candles)
    assert signal is None


def test_rechazo_por_datos_insuficientes():
    candles = [make_candle(1.0, 10.0, i) for i in range(10)]
    assert detectar_tendencia(candles) == "neutral"
    assert generar_pre_senal(candles) is None

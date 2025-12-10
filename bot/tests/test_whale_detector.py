import pytest
import math

from bot.core.whale_detector import (
    detectar_volumen_extremo,
    detectar_fast_move,
    detectar_stop_hunt,
    detectar_squeeze,
    detectar_whale_trade,
    clasificar_severidad,
    analizar_ballenas,
)


def test_volumen_extremo_detectado():
    candles = [{"volume": 10} for _ in range(20)]
    candles.append({"volume": 100})
    assert detectar_volumen_extremo(candles, factor=2.0) is True


def test_volumen_extremo_no_detectado():
    candles = [{"volume": 10} for _ in range(21)]
    assert detectar_volumen_extremo(candles, factor=2.0) is False


def test_fast_move_detectado():
    candles = [{"close": 100}, {"close": 102}]
    assert detectar_fast_move(candles, threshold_pct=0.01) is True


def test_fast_move_no_detectado():
    candles = [{"close": 100}, {"close": 100.5}]
    assert detectar_fast_move(candles, threshold_pct=0.01) is False


def test_stop_hunt_mecha_larga_superior():
    candles = [{
        "open": 100, "close": 101,
        "high": 120, "low": 99
    }]
    assert detectar_stop_hunt(candles) is True


def test_stop_hunt_mecha_larga_inferior():
    candles = [{
        "open": 101, "close": 100,
        "high": 102, "low": 80
    }]
    assert detectar_stop_hunt(candles) is True


def test_whale_trade_detectado():
    candles = [{"open": 100, "close": 101} for _ in range(20)]
    candles.append({"open": 100, "close": 120})
    assert detectar_whale_trade(candles, trade_factor=2.0) is True


def test_whale_trade_no_detectado():
    candles = [{"open": 100, "close": 101} for _ in range(21)]
    assert detectar_whale_trade(candles, trade_factor=2.0) is False


def test_squeeze_detectado():
    candles = []
    # compresión
    for i in range(30):
        candles.append({"open": 100, "close": 100.3, "high": 100.4, "low": 100.2})
    # expansión
    candles.append({"open": 100, "close": 103, "high": 104, "low": 99})
    assert detectar_squeeze(candles) is True


def test_squeeze_no_detectado():
    candles = []
    for i in range(60):
        candles.append({"open": 100, "close": 100.5, "high": 101, "low": 100})
    assert detectar_squeeze(candles) is False


def test_clasificar_severidad_alta():
    eventos = {
        "volume_spike": True,
        "whale_trade": True,
        "fast_move": True,
        "stop_hunt": False,
        "squeeze": False,
    }
    assert clasificar_severidad(eventos) == "high"


def test_clasificar_severidad_media():
    eventos = {
        "volume_spike": True,
        "whale_trade": True,
        "fast_move": False,
        "stop_hunt": False,
        "squeeze": False,
    }
    assert clasificar_severidad(eventos) == "medium"


def test_clasificar_severidad_baja():
    eventos = {
        "volume_spike": False,
        "whale_trade": False,
        "fast_move": True,
        "stop_hunt": False,
        "squeeze": False,
    }
    assert clasificar_severidad(eventos) == "low"


def test_analizar_ballenas_integration():
    candles = []
    for i in range(20):
        candles.append({"open": 100, "close": 100, "high": 100, "low": 100, "volume": 10})
    candles.append({"open": 100, "close": 105, "high": 110, "low": 95, "volume": 200})
    resultado = analizar_ballenas(candles)
    assert isinstance(resultado, dict)
    assert "severity" in resultado
    assert "razones" in resultado
    assert resultado["severity"] in ("low", "medium", "high")
    assert all(isinstance(r, str) for r in resultado["razones"])

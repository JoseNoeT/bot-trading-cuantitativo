import math
import pytest

from bot.core.signal_engine import (
    analizar_ballenas,
    generar_senal_final,
)
from bot.core.strategy import generar_pre_senal
from bot.core.risk_manager import aplicar_filtros_riesgo


def _make_increasing_candles(count=59, base_volume=50, big_volume=200):
    candles = []
    for i, p in enumerate(range(1, count + 1)):
        candles.append({
            "open": p - 1,
            "high": p,
            "low": p - 1,
            "close": p,
            "volume": base_volume,
            "timestamp": i,
        })
    candles[-1]["volume"] = big_volume
    return candles


def _make_decreasing_candles(count=59, base_volume=50, big_volume=200, start=100):
    candles = []
    # create a descending sequence
    for i, p in enumerate(range(start, start - count, -1)):
        candles.append({
            "open": p + 1,
            "high": p + 1,
            "low": p,
            "close": p,
            "volume": base_volume,
            "timestamp": i,
        })
    candles[-1]["volume"] = big_volume
    return candles


def test_analizar_ballenas_sin_alertas():
    eventos = {
        "volume_spike": False,
        "whale_trade": False,
        "fast_move": False,
        "stop_hunt": False,
        "squeeze": False,
        "severity": "low",
    }
    resultado = analizar_ballenas(eventos)
    assert resultado["alerta_ballenas"] is False
    assert isinstance(resultado["razon_ballenas"], list)


def test_analizar_ballenas_severidad_alta():
    eventos = {
        "volume_spike": False,
        "whale_trade": False,
        "fast_move": False,
        "stop_hunt": False,
        "squeeze": False,
        "severity": "high",
    }
    resultado = analizar_ballenas(eventos)
    assert resultado["alerta_ballenas"] is True


def test_analizar_ballenas_multiples_eventos():
    eventos = {
        "volume_spike": True,
        "whale_trade": True,
        "fast_move": False,
        "stop_hunt": False,
        "squeeze": False,
        "severity": "low",
    }
    resultado = analizar_ballenas(eventos)
    assert resultado["alerta_ballenas"] is True
    assert len(resultado["razon_ballenas"]) >= 2


def test_generar_senal_final_long_valida():
    candles = _make_increasing_candles()

    configs = {
        "symbol": "TESTUSDT",
        "risk_per_trade": 0.01,
        "max_daily_loss": 0.10,
        "max_trades_per_day": 5,
        "max_volatility_pct": 0.05,
        "volume_factor_confirm": 1.5,
    }

    estado = {"balance": 1000, "perdidas_acumuladas": 0.0, "operaciones_hoy": 1}

    resultado = generar_senal_final(candles, estado, configs, eventos_ballenas=None)
    assert resultado is not None
    assert resultado["direction"] == "LONG"
    assert resultado["sl"] < resultado["entry"]
    assert resultado["tp"] > resultado["entry"]
    assert "confidence" in resultado
    assert 0.0 <= resultado["confidence"] <= 1.0


def test_generar_senal_final_short_valida():
    candles = _make_decreasing_candles()

    configs = {
        "symbol": "TESTUSDT",
        "risk_per_trade": 0.01,
        "max_daily_loss": 0.10,
        "max_trades_per_day": 5,
        "max_volatility_pct": 0.05,
        "volume_factor_confirm": 1.5,
    }

    estado = {"balance": 1000, "perdidas_acumuladas": 0.0, "operaciones_hoy": 1}

    resultado = generar_senal_final(candles, estado, configs, eventos_ballenas=None)
    assert resultado is not None
    assert resultado["direction"] == "SHORT"
    assert resultado["sl"] > resultado["entry"]
    assert resultado["tp"] < resultado["entry"]


def test_rechazo_por_ballenas():
    candles = _make_increasing_candles()
    configs = {
        "symbol": "TESTUSDT",
        "risk_per_trade": 0.01,
        "max_daily_loss": 0.10,
        "max_trades_per_day": 5,
        "max_volatility_pct": 0.05,
    }
    estado = {"balance": 1000, "perdidas_acumuladas": 0.0, "operaciones_hoy": 1}
    eventos = {
        "volume_spike": True,
        "whale_trade": True,
        "fast_move": False,
        "stop_hunt": False,
        "squeeze": False,
        "severity": "high",
    }

    resultado = generar_senal_final(candles, estado, configs, eventos)
    assert resultado is None


def test_rechazo_por_riesgo_volatilidad_alta():
    candles = _make_increasing_candles()
    # Make last candle extremely volatile
    candles[-1]["high"] = candles[-1]["close"] + 50
    candles[-1]["low"] = candles[-1]["close"] - 50

    configs = {
        "symbol": "TESTUSDT",
        "risk_per_trade": 0.01,
        "max_daily_loss": 0.10,
        "max_trades_per_day": 5,
        "max_volatility_pct": 0.01,  # tighten to force rejection
    }
    estado = {"balance": 1000, "perdidas_acumuladas": 0.0, "operaciones_hoy": 1}

    resultado = generar_senal_final(candles, estado, configs, eventos_ballenas=None)
    assert resultado is None


def test_rechazo_por_max_operaciones():
    candles = _make_increasing_candles()
    configs = {
        "symbol": "TESTUSDT",
        "risk_per_trade": 0.01,
        "max_daily_loss": 0.10,
        "max_trades_per_day": 5,
        "max_volatility_pct": 0.05,
    }
    estado = {"balance": 1000, "perdidas_acumuladas": 0.0, "operaciones_hoy": 10}

    resultado = generar_senal_final(candles, estado, configs, None)
    assert resultado is None


def test_estructura_completa_de_senal():
    candles = _make_increasing_candles()
    configs = {
        "symbol": "TESTUSDT",
        "risk_per_trade": 0.01,
        "max_daily_loss": 0.10,
        "max_trades_per_day": 5,
        "max_volatility_pct": 0.05,
    }
    estado = {"balance": 1000, "perdidas_acumuladas": 0.0, "operaciones_hoy": 1}

    s = generar_senal_final(candles, estado, configs, None)
    assert s is not None
    assert "symbol" in s
    assert "entry" in s
    assert "sl" in s
    assert "tp" in s
    assert "position_size" in s
    assert isinstance(s["reasons"], list)
    assert isinstance(s["ballena_flags"], dict)


def test_integracion_modulos():
    # smoke test to ensure strategy and risk modules pueden integrarse
    candles = _make_increasing_candles()
    pre = generar_pre_senal(candles)
    assert isinstance(pre, dict) or pre is None

    configs = {
        "symbol": "TESTUSDT",
        "risk_per_trade": 0.01,
        "max_daily_loss": 0.10,
        "max_trades_per_day": 5,
        "max_volatility_pct": 0.05,
    }
    estado = {"balance": 1000, "perdidas_acumuladas": 0.0, "operaciones_hoy": 1}

    if pre:
        filtered = aplicar_filtros_riesgo(pre, estado, configs)
        # filtered puede ser dict con position_size o None
        assert filtered is None or isinstance(filtered, dict)

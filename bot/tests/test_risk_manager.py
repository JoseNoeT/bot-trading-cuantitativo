"""
Tests unitarios para risk_manager.py
FASE 3 — Gestión de Riesgo
Autor: José Miguel Noé Torres
"""

import pytest
import math

from bot.core.risk_manager import (
    calcular_tamano_posicion,
    validar_sl_tp,
    excede_perdida_diaria,
    excede_max_operaciones,
    validar_volatilidad,
    aplicar_filtros_riesgo,
)


def test_calcular_tamano_posicion_basico():
    balance = 1000
    riesgo = 0.01  # 1% → 10 USDT
    sl_distancia = 2.0
    size = calcular_tamano_posicion(balance, riesgo, sl_distancia)
    assert size == pytest.approx(5.0)


def test_calcular_tamano_posicion_errores():
    with pytest.raises(ValueError):
        calcular_tamano_posicion(1000, -0.01, 2.0)
    with pytest.raises(ValueError):
        calcular_tamano_posicion(1000, 0.01, 0)
    with pytest.raises(ValueError):
        calcular_tamano_posicion(-1000, 0.01, 2.0)


def test_validar_sl_tp_long_ok():
    entry = 100.0
    sl = 95.0
    tp = 110.0
    assert validar_sl_tp(entry, sl, tp, direction="LONG") is True


def test_validar_sl_tp_short_ok():
    entry = 100.0
    sl = 105.0
    tp = 90.0
    assert validar_sl_tp(entry, sl, tp, direction="SHORT") is True


def test_validar_sl_tp_rr_insuficiente():
    entry = 100.0
    sl = 95.0
    tp = 100.0  # TP distance 0 -> invalid
    assert validar_sl_tp(entry, sl, tp, direction="LONG") is False
    # RR 1:1 case
    tp2 = 105.0
    assert validar_sl_tp(entry, sl, tp2, direction="LONG") is False


def test_validar_volatilidad():
    assert validar_volatilidad(atr=1.0, max_volatilidad_pct=0.05, entry_price=100.0) is True
    assert validar_volatilidad(atr=10.0, max_volatilidad_pct=0.05, entry_price=100.0) is False


def test_excede_perdida_diaria():
    assert excede_perdida_diaria(0.05, 0.03) is True
    assert excede_perdida_diaria(0.01, 0.03) is False


def test_excede_max_operaciones():
    assert excede_max_operaciones(6, 5) is True
    assert excede_max_operaciones(3, 5) is False


def make_pre_senal(direction="LONG", entry=100.0, atr=2.0):
    return {
        "direction": direction,
        "entry_price": entry,
        "atr": atr,
        "timestamp": 12345,
        "reason": [],
    }


def test_aplicar_filtros_riesgo_valida_long():
    pre_senal = make_pre_senal("LONG", 100.0, 2.0)
    configs = {
        "risk_per_trade": 0.01,
        "max_daily_loss": 0.05,
        "max_trades_per_day": 5,
        "max_volatility_pct": 0.05,
    }
    estado = {"balance": 1000.0, "perdidas_acumuladas": 0.0, "operaciones_hoy": 1}
    resultado = aplicar_filtros_riesgo(pre_senal, estado, configs)
    assert resultado is not None
    assert resultado["direction"] == "LONG"
    assert resultado["sl"] < resultado["entry"]
    assert resultado["tp"] > resultado["entry"]


def test_aplicar_filtros_riesgo_rechazo_volatilidad():
    pre_senal = make_pre_senal("LONG", 100.0, 50.0)
    configs = {"risk_per_trade": 0.01, "max_daily_loss": 0.05, "max_trades_per_day": 5, "max_volatility_pct": 0.05}
    estado = {"balance": 1000.0, "perdidas_acumuladas": 0.0, "operaciones_hoy": 1}
    assert aplicar_filtros_riesgo(pre_senal, estado, configs) is None


def test_aplicar_filtros_riesgo_rechazo_perdida_diaria():
    pre_senal = make_pre_senal("LONG", 100.0, 2.0)
    configs = {"risk_per_trade": 0.01, "max_daily_loss": 0.05, "max_trades_per_day": 5, "max_volatility_pct": 0.05}
    estado = {"balance": 1000.0, "perdidas_acumuladas": 0.10, "operaciones_hoy": 1}
    assert aplicar_filtros_riesgo(pre_senal, estado, configs) is None


def test_aplicar_filtros_riesgo_rechazo_max_operaciones():
    pre_senal = make_pre_senal("LONG", 100.0, 2.0)
    configs = {"risk_per_trade": 0.01, "max_daily_loss": 0.05, "max_trades_per_day": 5, "max_volatility_pct": 0.05}
    estado = {"balance": 1000.0, "perdidas_acumuladas": 0.0, "operaciones_hoy": 10}
    assert aplicar_filtros_riesgo(pre_senal, estado, configs) is None


def test_aplicar_filtros_riesgo_rechazo_rr_insuficiente():
    # ATR muy pequeño -> sl_distancia pequeña -> TP too close -> RR < 2
    pre_senal = make_pre_senal("LONG", 100.0, 0.1)
    configs = {"risk_per_trade": 0.01, "max_daily_loss": 0.05, "max_trades_per_day": 5, "max_volatility_pct": 0.05}
    estado = {"balance": 1000.0, "perdidas_acumuladas": 0.0, "operaciones_hoy": 0}
    # Because ATR small, the TP will be only 0.2 away while SL 0.15 away → RR 1.333 < 2
    assert aplicar_filtros_riesgo(pre_senal, estado, configs) is None

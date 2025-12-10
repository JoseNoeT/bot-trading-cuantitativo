"""
risk_manager.py
Módulo de gestión de riesgo.
Referencias: docs/05_Gestion_de_Riesgo.md
"""
from __future__ import annotations

import math
from typing import Dict, Optional


def calcular_tamano_posicion(balance: float, riesgo_por_trade: float, sl_distancia: float) -> float:
    """Calcula el tamaño de la posición en unidades de moneda.

    Fórmula:
        riesgo_monetario = balance * riesgo_por_trade
        posicion = riesgo_monetario / sl_distancia

    Args:
        balance: capital disponible (en la misma moneda que la posición, p.ej. USDT).
        riesgo_por_trade: fracción del balance a arriesgar (ej. 0.01 = 1%).
        sl_distancia: distancia entre entry y SL (en unidades de precio).

    Returns:
        Tamaño de posición (en unidades monetarias) como float.

    Raises:
        ValueError: si sl_distancia <= 0 o riesgo_por_trade <= 0.
    """
    if sl_distancia <= 0:
        raise ValueError("sl_distancia must be > 0")
    if riesgo_por_trade <= 0:
        raise ValueError("riesgo_por_trade must be > 0")
    if balance <= 0:
        raise ValueError("balance must be > 0")
    riesgo_monetario = float(balance) * float(riesgo_por_trade)
    posicion = riesgo_monetario / float(sl_distancia)
    return float(posicion)


def validar_sl_tp(entry: float, sl: float, tp: float, direction: str, min_rr: float = 2.0) -> bool:
    """Valida que SL y TP estén en los lados correctos y respeten ratio mínimo.

    Args:
        entry: precio de entrada.
        sl: precio del stop loss.
        tp: precio del take profit.
        direction: 'LONG' o 'SHORT'.
        min_rr: ratio mínimo TP/SL (default 2.0 -> 1:2).

    Returns:
        True si SL/TP válidos según reglas, False en caso contrario.
    """
    if direction not in ("LONG", "SHORT"):
        return False

    if direction == "LONG":
        # SL debe ser menor que entry, TP mayor que entry
        if not (sl < entry < tp):
            return False
        sl_distance = entry - sl
        tp_distance = tp - entry
    else:
        # SHORT: SL debe ser mayor que entry, TP menor que entry
        if not (tp < entry < sl):
            return False
        sl_distance = sl - entry
        tp_distance = entry - tp

    if sl_distance <= 0 or tp_distance <= 0:
        return False

    # Ratio TP/SL debe ser >= min_rr
    if (tp_distance / sl_distance) < float(min_rr):
        return False

    return True


def excede_perdida_diaria(perdidas_acumuladas: float, max_perdida_diaria: float) -> bool:
    """Devuelve True si las pérdidas acumuladas alcanzan o superan el máximo permitido."""
    try:
        return float(perdidas_acumuladas) >= float(max_perdida_diaria)
    except Exception:
        return False


def excede_max_operaciones(operaciones_hoy: int, max_operaciones: int) -> bool:
    """Devuelve True si ya se alcanzó el número máximo de operaciones permitidas hoy."""
    try:
        return int(operaciones_hoy) >= int(max_operaciones)
    except Exception:
        return False


def validar_volatilidad(atr: float, max_volatilidad_pct: float, entry_price: float) -> bool:
    """Valida que la volatilidad (medida por ATR) no exceda el umbral relativo.

    Args:
        atr: valor de ATR en unidades de precio.
        max_volatilidad_pct: máximo tolerado como fracción (ej. 0.025 = 2.5%).
        entry_price: precio de entrada.

    Returns:
        True si la volatilidad está dentro del límite, False si es excesiva.
    """
    try:
        if entry_price <= 0:
            return False
        ratio = float(atr) / float(entry_price)
        return ratio <= float(max_volatilidad_pct)
    except Exception:
        return False


def aplicar_filtros_riesgo(pre_senal: Dict, estado_riesgo: Dict, configs: Dict) -> Optional[Dict]:
    """Aplica las reglas de riesgo a una pre-señal y devuelve una señal validada o None.

    Args:
        pre_senal: diccionario generado por `strategy.generar_pre_senal`.
        estado_riesgo: diccionario con el estado actual, p.ej. {
            "balance": float,
            "perdidas_acumuladas": float,
            "operaciones_hoy": int
        }
        configs: diccionario con parámetros de riesgo, p.ej. {
            "risk_per_trade": 0.01,
            "max_daily_loss": 0.03,
            "max_trades_per_day": 5,
            "max_volatility_pct": 0.025
        }

    Returns:
        Diccionario con la señal final y tamaño de posición, o None si se rechaza.
    """
    # Validaciones básicas de inputs
    if not pre_senal:
        return None
    direction = pre_senal.get("direction")
    entry = pre_senal.get("entry_price") or pre_senal.get("entry")
    atr = pre_senal.get("atr")
    if direction not in ("LONG", "SHORT") or entry is None or atr is None:
        return None

    # No aceptar atr NaN
    if atr is None or (isinstance(atr, float) and math.isnan(atr)):
        return None

    # Configs y estado con valores por defecto seguros
    riesgo_por_trade = float(configs.get("risk_per_trade", 0.01))
    max_daily_loss = float(configs.get("max_daily_loss", 0.03))
    max_trades = int(configs.get("max_trades_per_day", 5))
    max_vol_pct = float(configs.get("max_volatility_pct", 0.025))

    balance = float(estado_riesgo.get("balance", 0.0))
    perdidas_acumuladas = float(estado_riesgo.get("perdidas_acumuladas", 0.0))
    operaciones_hoy = int(estado_riesgo.get("operaciones_hoy", 0))

    reasons = []

    # 1) Verificar pérdida diaria
    if excede_perdida_diaria(perdidas_acumuladas, max_daily_loss):
        reasons.append("excede perdida diaria")
        return None

    # 2) Verificar número de operaciones hoy
    if excede_max_operaciones(operaciones_hoy, max_trades):
        reasons.append("excede max operaciones diarias")
        return None

    # 3) Calcular distancia SL y SL/TP
    sl_distancia = 1.5 * float(atr)
    if sl_distancia <= 0:
        reasons.append("sl_distancia invalida")
        return None

    entry_price = float(entry)
    if direction == "LONG":
        sl = entry_price - sl_distancia
        tp = entry_price + (sl_distancia * 2.0)
    else:
        sl = entry_price + sl_distancia
        tp = entry_price - (sl_distancia * 2.0)

    # 4) Validar SL/TP
    if not validar_sl_tp(entry_price, sl, tp, direction):
        reasons.append("sl/tp invalidos")
        return None

    # 5) Validar volatilidad relativa
    if not validar_volatilidad(float(atr), max_vol_pct, entry_price):
        reasons.append("volatilidad excesiva")
        return None

    # 6) Calcular tamaño de posición
    try:
        posicion = calcular_tamano_posicion(balance, riesgo_por_trade, sl_distancia)
    except ValueError:
        reasons.append("parametros de riesgo invalidos")
        return None

    # Construir resultado sin modificar objetos originales
    result = {
        "direction": direction,
        "entry": entry_price,
        "sl": float(sl),
        "tp": float(tp),
        "atr": float(atr),
        "position_size": float(posicion),
        "reason": reasons or ["ok"],
    }
    return result


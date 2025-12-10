"""
signal_engine.py
Ensambla la pre-señal (strategy) + filtros de riesgo + análisis de ballenas
para producir la señal final lista para el panel/alertas.

Funciones principales:
- analizar_ballenas(eventos: dict) -> dict
- generar_senal_final(candles, estado_riesgo, configs, eventos_ballenas) -> dict | None

Referencias: docs/03_Modulos_Core.md, docs/04_Estrategia_Base.md,
docs/05_Gestion_de_Riesgo.md, docs/06_Radar_de_Ballenas.md
"""

from __future__ import annotations

import math
from typing import Dict, List, Optional

from bot.core.strategy import generar_pre_senal
from bot.core.risk_manager import aplicar_filtros_riesgo


def analizar_ballenas(eventos: Dict) -> Dict:
    """Analiza un dict de eventos del radar de ballenas y decide si activar alerta.

    Args:
        eventos: dict con claves booleanas y 'severity'. Ejemplo:
            {"volume_spike": True, "whale_trade": False, "fast_move": False, ...}

    Returns:
        {"alerta_ballenas": bool, "razon_ballenas": [str, ...]}
    """
    if not eventos:
        return {"alerta_ballenas": False, "razon_ballenas": []}

    reasons: List[str] = []
    alert = False

    severity = eventos.get("severity")
    if severity == "high":
        reasons.append("severity high")
        alert = True

    # Count truthy event flags (excluding severity)
    flags = [
        "volume_spike",
        "whale_trade",
        "fast_move",
        "stop_hunt",
        "squeeze",
    ]
    true_flags = [f for f in flags if bool(eventos.get(f))]
    for f in true_flags:
        reasons.append(f)

    # If two or more distinct events -> alert
    if len(true_flags) >= 2:
        alert = True

    # If only a single small volume spike with low severity -> don't alert (tag only)
    if len(true_flags) == 1 and true_flags[0] == "volume_spike" and severity in (None, "low"):
        alert = False

    return {"alerta_ballenas": alert, "razon_ballenas": reasons}


def _confidence_from_reasons(pre_reasons: List[str], risk_reasons: List[str], ballenas: Dict, configs: Dict) -> float:
    """Heurística simple para asignar un score de confianza entre 0.0 y 1.0.

    Suma ponderada de características discretas (cada +0.2), luego recortar.
    """
    score = 0.0

    # volumen fuerte en pre_reasons (busca 'volumen x{factor}')
    vol_factor = 0.0
    for r in pre_reasons:
        if r.startswith("volumen x"):
            try:
                vol_factor = float(r.split("x")[1])
            except Exception:
                vol_factor = 0.0
    if vol_factor >= float(configs.get("volume_factor_confirm", 1.5)):
        score += 0.2

    # tendencia fuerte: buscar 'EMA20/EMA50 separadas' en pre_reasons
    combined_reasons = pre_reasons + (risk_reasons or [])
    if any("EMA20/EMA50 separadas" in r for r in combined_reasons):
        score += 0.2

    # volatilidad baja-normal: comparar atr/entry vs max_volatility_pct
    atr = None
    entry = None
    for r in (risk_reasons or []):
        pass
    # attempt to read from configs if provided
    max_vol_pct = float(configs.get("max_volatility_pct", configs.get("max_volatility_pct", 0.025)))
    # we expect caller to pass atr and entry separately; fallback to 0
    # this function is called with available context by generar_senal_final

    # ballenas absent -> +0.2
    if not ballenas or not ballenas.get("alerta_ballenas"):
        score += 0.2

    # SL/TP RR check will be computed in caller and passed via risk_reasons
    if any("rr_good" in r for r in (risk_reasons or [])):
        score += 0.2

    # Clamp
    if score < 0.0:
        score = 0.0
    if score > 1.0:
        score = 1.0
    return round(score, 2)


def generar_senal_final(candles: List[Dict], estado_riesgo: Dict, configs: Dict, eventos_ballenas: Optional[Dict] = None) -> Optional[Dict]:
    """Función principal que genera la señal final combinando strategy, risk y ballenas.

    Args:
        candles: lista de velas (estructura definida en strategy.py).
        estado_riesgo: estado con balance, perdidas_acumuladas, operaciones_hoy.
        configs: configuraciones (contiene 'symbol' y parámetros de risk).
        eventos_ballenas: dict opcional con eventos detectados por whale_detector.

    Returns:
        Señal final (dict) o None si se descarta.
    """
    # PASO 1 — Obtener pre-señal
    pre = generar_pre_senal(candles)
    if not pre:
        return None

    # PASO 2 — Analizar ballenas
    ballenas = analizar_ballenas(eventos_ballenas or {})
    # Si hay alerta fuerte, rechazar
    if ballenas.get("alerta_ballenas"):
        # attach reason to pre reason copy and return None
        return None

    # PASO 3 — Validar riesgo
    senal_riesgo = aplicar_filtros_riesgo(pre, estado_riesgo, configs)
    if not senal_riesgo:
        return None

    # PASO 4 — Ensamblar señal final
    symbol = configs.get("symbol", "UNKNOWN")
    entry = float(senal_riesgo["entry"])
    sl = float(senal_riesgo["sl"])
    tp = float(senal_riesgo["tp"])
    position_size = float(senal_riesgo["position_size"])
    atr = float(senal_riesgo.get("atr") or 0.0)
    timestamp = int(pre.get("timestamp", 0))

    # reasons: combine pre and risk reasons into a new list
    reasons: List[str] = []
    reasons.extend(list(pre.get("reason") or []))
    reasons.extend(list(senal_riesgo.get("reason") or []))

    # PASO 5 — Calcular confianza
    # Determine rr goodness
    rr_good = False
    try:
        if senal_riesgo["direction"] == "LONG":
            sl_dist = entry - sl
            tp_dist = tp - entry
        else:
            sl_dist = sl - entry
            tp_dist = entry - tp
        rr = (tp_dist / sl_dist) if sl_dist > 0 else 0.0
        if rr >= 2.0:
            rr_good = True
            reasons.append("rr_good")
    except Exception:
        rr = 0.0

    # Build risk_reasons shorthand
    risk_reasons = list(senal_riesgo.get("reason") or [])

    # Augment reasons with ballena info
    ballena_flags = ballenas

    # Compute score components
    score = 0.0
    # volumen fuerte
    vol_factor = 0.0
    for r in pre.get("reason") or []:
        if isinstance(r, str) and r.startswith("volumen x"):
            try:
                vol_factor = float(r.split("x")[1])
            except Exception:
                vol_factor = 0.0
    if vol_factor >= float(configs.get("volume_factor_confirm", 1.5)):
        score += 0.2

    # tendencia fuerte
    if any("EMA20/EMA50 separadas" in str(r) for r in pre.get("reason") or []):
        score += 0.2

    # volatilidad baja-normal
    max_vol_pct = float(configs.get("max_volatility_pct", 0.025))
    if atr > 0 and (atr / entry) <= max_vol_pct:
        score += 0.2

    # sin señales de ballenas
    if not ballena_flags.get("alerta_ballenas"):
        score += 0.2

    # SL/TP con buen RR
    if rr_good:
        score += 0.2

    # Clamp score
    confidence = max(0.0, min(1.0, round(score, 2)))

    final = {
        "symbol": symbol,
        "direction": senal_riesgo["direction"],
        "entry": entry,
        "sl": sl,
        "tp": tp,
        "position_size": position_size,
        "atr": atr,
        "timestamp": timestamp,
        "reasons": reasons,
        "ballena_flags": ballena_flags,
        "confidence": confidence,
    }

    return final


__all__ = ["analizar_ballenas", "generar_senal_final"]
"""
signal_engine.py
Motor que combina estrategia, riesgo y detección de ballenas para emitir señales finales.
Referencias: docs/03_Modulos_Core.md
"""

def placeholder():
    """Placeholder para el signal engine.

    Implementar flujo de validación en FASE 2/3.
    """
    return None

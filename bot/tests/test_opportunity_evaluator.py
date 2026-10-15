"""Pruebas puras del primer evaluador de oportunidades Spot."""
import pytest
from bot.opportunities.evaluator import evaluate_spot_opportunity


def market(trends):
    return {"symbol": "WLDUSDT", "source": "BINANCE_PUBLIC_REST",
            "timeframes": {tf: {"trend": trend} for tf, trend in zip(("1d", "4h", "1h", "15m"), trends)}}


def test_downtrend_refuses_impulsive_buy():
    out = evaluate_spot_opportunity(market(["alcista", "bajista", "bajista", "bajista"]))
    assert out["state"] == "EVITAR_COMPRAS_IMPULSIVAS"
    assert out["action"] == "NO_OPERAR"
    assert not out["execution_enabled"]


def test_aligned_uptrend_still_requires_evidence():
    out = evaluate_spot_opportunity(market(["alcista"] * 4))
    assert out["state"] == "OBSERVAR_CONFIGURACION_ALCISTA"
    assert out["action"] == "NO_OPERAR"
    assert out["evidence"] == "HEURISTIC_NOT_BACKTESTED"


def test_missing_candles_context_fails_closed():
    with pytest.raises(ValueError, match="Temporalidades"):
        evaluate_spot_opportunity({"symbol": "WLDUSDT", "source": "BINANCE_PUBLIC_REST"})


def test_invalid_radar_cannot_assert_whale():
    with pytest.raises(ValueError, match="ballenas"):
        evaluate_spot_opportunity(market(["neutral"] * 4),
            {"symbol": "WLDUSDT", "source": "BINANCE_PUBLIC_REST", "whale_confirmed": True})

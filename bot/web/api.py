"""API de demostracion del copiloto: solo datos sinteticos, sin exchange real."""
from __future__ import annotations

from datetime import datetime, timezone
from fastapi import FastAPI
from bot.core.signal_engine import generar_senal_final

app = FastAPI(title="BotTrading Copiloto", version="0.1.0")


def synthetic_candles(count: int = 60) -> list[dict]:
    """Datos deterministas para demostracion. NO representan precios reales."""
    candles = []
    for i in range(count):
        p = 100.0 + i
        candles.append({
            "open": p - 1.0,
            "high": p + 0.5,
            "low": p - 1.5,
            "close": p,
            "volume": 50.0,
            "timestamp": i,
        })
    candles[-1]["volume"] = 200.0
    return candles


def build_snapshot() -> dict:
    config = {
        "symbol": "DEMOUSDT",
        "risk_per_trade": 0.01,
        "max_daily_loss": 0.03,
        "max_trades_per_day": 5,
        "max_volatility_pct": 0.05,
        "volume_factor_confirm": 1.5,
    }
    # Riesgo nulo en la demo. La aplicacion no acepta saldo del usuario.
    # En modo real el estado financiero debera validarse contra un ledger persistente.
    estado = {"balance": 1000.0, "perdidas_acumuladas": 0.0, "operaciones_hoy": 0}
    signal = generar_senal_final(synthetic_candles(), estado, config)
    return {
        "mode": "SIMULATION_ONLY",
        "source": "SYNTHETIC_DATA",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "real_orders_enabled": False,
        "authorization": "REQUIRED_FOR_ANY_FUTURE_REAL_ORDER",
        "signal": signal,
        "note": "La confianza es heuristica, NO probabilidad de beneficio.",
    }


@app.get("/")
def root() -> dict:
    return {
        "name": "BotTrading Copiloto",
        "mode": "SIMULATION_ONLY",
        "routes": ["/health", "/demo/signal", "/docs"],
    }


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "mode": "SIMULATION_ONLY", "exchange_connected": False}


@app.get("/demo/signal")
def demo_signal() -> dict:
    return build_snapshot()

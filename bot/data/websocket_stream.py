"""bot/data/websocket_stream.py
Cliente WebSocket para consumir streams públicos de Binance y reenviarlos a un ConnectionManager.

Funcionalidad:
- Conexión al stream combinado público (spot) de Binance via websockets.
- Reconexión con backoff en errores.
- Parseo básico de mensajes de trade y reenvío en formato simple.

Notas:
- No se requieren API keys para streams públicos de trades.
"""
import asyncio
import json
import logging
from typing import Iterable

import websockets

logger = logging.getLogger(__name__)


def _build_combined_url(symbols: Iterable[str], stream_type: str = "spot") -> str:
    # symbols expected like ['btcusdt','ethusdt'] (lowercase)
    base = "wss://stream.binance.com:9443/stream" if stream_type == "spot" else "wss://fstream.binance.com/stream"
    streams = "/".join(f"{s}@trade" for s in symbols)
    return f"{base}?streams={streams}"


async def forward_trades(mgr, symbols=None, stream_type: str = "spot"):
    """Conecta al stream combinado y reenvía eventos 'trade' al manager.

    mgr debe exponer un método async `broadcast(dict)`.
    """
    if symbols is None:
        symbols = ["btcusdt", "ethusdt"]
    symbols = [s.lower() for s in symbols]

    url = _build_combined_url(symbols, stream_type=stream_type)
    backoff = 1.0
    max_backoff = 60.0

    while True:
        try:
            logger.info("Connecting to Binance stream %s", url)
            async with websockets.connect(url, ping_interval=20, ping_timeout=10) as ws:
                logger.info("Connected to Binance stream")
                backoff = 1.0
                async for raw in ws:
                    try:
                        obj = json.loads(raw)
                        # Binance combined stream wraps payload in 'data'
                        data = obj.get("data") or obj
                        # trade event has e == 'trade'
                        if data.get("e") == "trade":
                            symbol = data.get("s", "").upper()
                            price = float(data.get("p", 0))
                            qty = float(data.get("q", 0))
                            ts = int(data.get("T") / 1000) if data.get("T") else None
                            message = {
                                "ts": ts or int(asyncio.get_event_loop().time()),
                                "symbol": symbol,
                                "price": price,
                                "volume": qty,
                                "whale": False,
                                "raw": data,
                            }
                            # fire-and-forget broadcast
                            try:
                                await mgr.broadcast(message)
                            except Exception:
                                logger.exception("Error broadcasting message")
                    except json.JSONDecodeError:
                        logger.warning("Received non-json from binance stream")
        except Exception:
            logger.exception("Binance stream error, reconnecting in %.1fs", backoff)
            await asyncio.sleep(backoff)
            backoff = min(max_backoff, backoff * 2)

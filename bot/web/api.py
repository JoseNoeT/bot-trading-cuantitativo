"""bot/web/api.py
API mínima (FastAPI) para exponer endpoints básicos del bot.
Este módulo exporta una instancia `app` para que uvicorn pueda cargarlo
con: python -m uvicorn bot.web.api:app --host 0.0.0.0 --port 8000

Los endpoints son placeholders diseñados para permitir pruebas locales.
"""
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from typing import Any
import asyncio
import random
import time

app = FastAPI(title="Bot Trading API", version="0.1")

# Templates folder
templates = Jinja2Templates(directory="bot/web/templates")


@app.get("/", summary="Root")
def root() -> dict[str, Any]:
    return {"message": "Bot Trading API", "status": "ok"}


@app.get("/status", summary="Estado del servicio")
def status() -> dict[str, Any]:
    return {"status": "ok"}


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    """Renderiza un dashboard HTML que se conecta al WebSocket `/ws/signals`."""
    return templates.TemplateResponse("index.html", {"request": request})


class ConnectionManager:
    def __init__(self):
        self.active: set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active.add(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active.discard(websocket)

    async def broadcast(self, message: dict):
        to_remove = []
        for ws in list(self.active):
            try:
                await ws.send_json(message)
            except Exception:
                to_remove.append(ws)
        for w in to_remove:
            self.disconnect(w)


mgr = ConnectionManager()

# Background task that simulates a market scanner and broadcasts signals
_scanner_task: asyncio.Task | None = None


async def scanner_loop():
    """Simula eventos/Señales de mercado y las difunde por WebSocket."""
    symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT"]
    while True:
        # Simular un pequeño delay entre eventos
        await asyncio.sleep(3)
        sig = {
            "ts": int(time.time()),
            "symbol": random.choice(symbols),
            "price": round(random.uniform(10_000, 70_000), 2),
            "volume": round(random.uniform(1, 2000), 2),
            "whale": random.random() < 0.05,
            "note": "simulated"
        }
        await mgr.broadcast(sig)


@app.on_event("startup")
async def start_scanner():
    global _scanner_task
    if _scanner_task is None:
        _scanner_task = asyncio.create_task(scanner_loop())


@app.on_event("shutdown")
async def stop_scanner():
    global _scanner_task
    if _scanner_task is not None:
        _scanner_task.cancel()
        try:
            await _scanner_task
        except asyncio.CancelledError:
            pass
        _scanner_task = None


@app.websocket("/ws/signals")
async def websocket_signals(websocket: WebSocket):
    await mgr.connect(websocket)
    try:
        while True:
            # Mantener la conexión abierta; esperamos mensajes del cliente si los hay
            await websocket.receive_text()
    except WebSocketDisconnect:
        mgr.disconnect(websocket)
    except Exception:
        mgr.disconnect(websocket)


@app.get("/signals", summary="Señales actuales (placeholder)")
def signals() -> dict[str, Any]:
    return {"signals": []}


@app.get("/metrics", summary="Métricas (placeholder)")
def metrics() -> dict[str, Any]:
    return {"metrics": {}}


@app.get("/settings", summary="Ajustes (placeholder)")
def settings() -> dict[str, Any]:
    return {"settings": {}}


@app.get("/logs", summary="Logs (placeholder)")
def logs() -> dict[str, Any]:
    return {"logs": []}


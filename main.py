"""BotTrading: ejecucion local segura, sin ordenes ni credenciales."""
from __future__ import annotations

import argparse
import json
from bot.web.api import build_snapshot


def main() -> None:
    parser = argparse.ArgumentParser(description="BotTrading copiloto en simulacion")
    parser.add_argument("--demo", action="store_true", help="mostrar una señal con datos sinteticos")
    parser.add_argument("--api", action="store_true", help="iniciar API FastAPI local")
    args = parser.parse_args()

    if args.api:
        import uvicorn
        uvicorn.run("bot.web.api:app", host="127.0.0.1", port=8000, reload=False)
    else:
        snapshot = build_snapshot()
        print(json.dumps(snapshot, indent=2, ensure_ascii=False))
        print("\nMODO SIMULACION: no se enviaron ordenes a Binance.")


if __name__ == "__main__":
    main()

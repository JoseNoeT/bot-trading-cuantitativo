# Dashboard y mercado público Binance

La rama `feature/binance-dashboard-integration` **reutiliza** el dashboard de
`feature/dashboard-ws`. No hay claves privadas, saldo de cuenta ni ejecución de órdenes.

## Windows / PowerShell
En la raíz del repositorio con `.venv` activo:

```powershell
python -m pip install -r requirements.txt
python -m pytest -q
$env:BOTTRADING_DATA_SOURCE = "simulation"
python -m uvicorn bot.web.api:app --host 127.0.0.1 --port 8000
```

Abre http://127.0.0.1:8000/dashboard y observa que el origen sea SIMULATION.

Para recibir trades públicos de Binance (solo lectura):

```powershell
$env:BOTTRADING_DATA_SOURCE = "binance"
python -m uvicorn bot.web.api:app --host 127.0.0.1 --port 8000
```

Debe indicar BINANCE y mostrar trades públicos de BTCUSDT/ETHUSDT si la conexión de
red y el acceso regional al WebSocket funcionan. Si no hay conexión, el cliente
registra reintentos y el panel puede quedar sin eventos; **no inventa precios**.

Endpoints: `/status`, `/source`, `/dashboard`, `/ws/signals`, `/docs`.
El nombre heredado `/ws/signals` aquí transporta *trades*, no señales LONG/SHORT.

## Pendientes
- Demostrar conectividad real WebSocket en entorno local.
- Añadir observabilidad de último evento y estado reconexión.
- Integrar velas cerradas y motor de señales; separar trades de señales.
- Armonizar el gestor de riesgo local y capital de referencia diario.
- Pruebas de integración sin red y validaciones extensivas del stream.

**Estado:** prototipo en revisión, no listo para trading real.

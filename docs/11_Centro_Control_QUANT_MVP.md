# Centro de control QUANT MVP

## UI
- `bot/web/templates/index.html`: estructura de tres vistas, sin lógica de cálculo.
- `bot/web/static/command_center.css`: sistema visual responsive.
- `bot/web/static/command_center.js`: controlador de mercado, contexto y radar; sin órdenes.
- `bot/web/static/order_review.js`: revisión manual de órdenes existente, aislada.

## Backend
- `bot/services/market_radar.py`: adaptador experimental de eventos de vela del módulo `bot/core/whale_detector.py`.
- `GET /radar/{symbol}`: devuelve volumen relativo, banderas de velas y limitaciones con `whale_confirmed=false` y `action=OBSERVAR`.
- El contexto 1D/4H/1H/15m se consulta por `GET /intelligence/{symbol}/multi`.

## Reglas de seguridad
- Ninguna ruta ejecuta órdenes; operaciones reales siguen deshabilitadas.
- El radar **no identifica ballenas** ni manipulación: es una aproximación experimental basada en velas.
- Se consulta en intervalos de 60 segundos; WebSocket público aporta transacciones visuales. No hay order book, ni análisis de microestructura de segundos, ni backtesting validado.
- El estado de una orden introducida manualmente no puede considerarse verificado.

## Verificación pendiente
1. `python -m pytest -q`.
2. Arrancar Uvicorn con `BOTTRADING_DATA_SOURCE=binance`.
3. Abrir `/dashboard` y comprobar Resumen / Órdenes / Mercado en vivo.
4. Abrir `/radar/WLDUSDT` y comprobar contrato y errores.
5. Mantener PR en borrador hasta verificar comportamiento real.

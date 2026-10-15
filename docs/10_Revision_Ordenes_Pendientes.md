# Revisión modular de órdenes Spot pendientes (solo lectura)

## Arquitectura
- `bot/orders/models.py`: entidad inmutable `PendingSpotOrder`, validaciones de cantidades y precio.
- `bot/orders/evaluator.py`: reglas deterministas y observaciones del contexto multitemporal.
- `bot/services/multitimeframe.py`: datos públicos con 1D, 4H, 1H y 15m; no accede al usuario.
- `bot/web/api.py`: adaptador HTTP POST /orders/review; solo acepta una orden introducida manualmente.
- `bot/tests/test_pending_order_review.py`: pruebas unitarias sin red.

## Ejemplo en /docs
POST /orders/review con cuerpo:

```json
{
  "symbol": "WLDUSDT",
  "side": "BUY",
  "quantity": "17.2",
  "limit_price": "0.4600"
}
```

## Seguridad y límites
La API **no consulta las órdenes privadas**, **no conoce si la orden sigue activa**, **no cancela ni envía órdenes**, **no accede al saldo**. El campo `order_status` siempre es `UNVERIFIED`. La respuesta `REVIEW_ONLY` describe riesgos de una orden introducida manualmente y no autoriza trading.

Pendiente: confirmar estado real por integración específica de solo lectura (si se autoriza), revisar costos, exposición y límites, backtesting y simulación. No fusionar hasta ejecutar pruebas y validar salida local.

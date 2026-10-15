# Copiloto supervisado: MVP local de demostración

## Alcance
Este MVP es **solo simulación**. No consulta la cuenta de Binance, no usa API keys,
no genera órdenes reales y no dispone de endpoint de ejecución.

## Iniciar desde la raíz del repositorio

```powershell
python -m pip install -r requirements.txt
python -m pip install pytest
python -m pytest -q
python main.py --demo
python main.py --api
```

La API se abre en `http://127.0.0.1:8000/docs`.

Endpoints:
- `GET /health`: estado local y confirmación de que Binance no está conectado.
- `GET /demo/signal`: señal generada por el núcleo cuantitativo a partir de velas sintéticas.
- `GET /`: rutas disponibles.

**Advertencia:** `DEMOUSDT` es un símbolo ficticio. Los precios y señales no son
cotizaciones reales ni recomendaciones de inversión. La puntuación de confianza
es heurística, no probabilidad de éxito.

## Integración futura
1. Validar calidad de datos y uso exclusivo de velas cerradas.
2. Conectar datos públicos Binance con control de caídas y reconexiones.
3. Unificar balance disponible, capital inicial del día y pérdidas monetarias.
4. Persistir estado y registro de decisiones; incorporar revisión humana con expiración.
5. Backtesting y paper trading con comisiones y deslizamiento.
6. Revisar mecanismos de protección antes de considerar cualquier operación real.

## Nota para desarrollo local
Si tienes cambios sin commit en `risk_manager.py`, guárdalos antes de
cambiar de rama o hacer merge. El PR evita modificar ese módulo para no
sobrescribir el trabajo local.

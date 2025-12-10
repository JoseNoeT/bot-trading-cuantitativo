# 📄 03_Modulos_Core.md
**BOT DE TRADING CUANTITATIVO — MÓDULOS CORE**  
Versión: 1.0  
Autor: José Miguel Noé Torres  

---

# 1. PROPÓSITO DEL DOCUMENTO
Definir la estructura detallada de los **módulos principales (CORE)** del bot de trading, que conforman el corazón lógico del sistema:

- Estrategia  
- Indicadores  
- Gestión de riesgo  
- Señales  
- Detección de ballenas  
- Motor de decisión  

Cada módulo será independiente, escalable y documentado para que Copilot pueda extenderlos sin romper arquitectura.

---

# 2. LISTA DE MÓDULOS CORE

Los módulos principales que conforman el núcleo del bot son:

1. `strategy.py`
2. `indicators.py`
3. `risk_manager.py`
4. `signal_engine.py`
5. `whale_detector.py`
6. `position_manager.py` (futuro)
7. `utils.py`

Cada uno cumple una función crítica en el pipeline cuantitativo.

---

# 3. DESCRIPCIÓN COMPLETA DE LOS MÓDULOS

---

## 🟦 3.1 strategy.py  
**Rol:** Aplicar la estrategia cuantitativa definida para generar señales preliminares.

### Funciones principales:
- `analyze_trend(candles)`  
- `calculate_entry(candles, indicators)`  
- `calculate_stoploss(price, atr)`  
- `calculate_takeprofit(entry, risk_reward)`  
- `generate_pre_signal(data)`  

### Lógica esperada:
- Usar EMA, volumen, volatilidad y estructura.  
- Determinar si el mercado está LONG, SHORT o neutral.  
- Combinar señales técnicas con validaciones de riesgo.

---

## 🟦 3.2 indicators.py  
**Rol:** Librería matemática del bot.

### Indicadores implementados:
- EMA, SMA  
- RSI  
- MACD  
- ATR  
- Volumen promedio  
- Volatilidad relativa  
- Detección de swings  

### Funciones base:
- `ema(values, length)`  
- `atr(high, low, close, length)`  
- `rs_index(close, length)`  
- `macd(close, fast, slow, signal)`  

Este módulo permite agregar nuevos indicadores sin tocar estrategia.

---

## 🟦 3.3 risk_manager.py  
**Rol:** Garantizar que TODAS las operaciones respeten reglas de seguridad.

### Funciones principales:
- `validate_signal(signal)`  
- `calculate_position_size(balance, risk_percent, sl_distance)`  
- `check_daily_loss_limit()`  
- `apply_risk_filters(signal)`  
- `block_trading_if_risky()`  

### Riesgos controlados:
- Tamaño de posición  
- Máxima pérdida diaria  
- Ratio SL/TP inválido  
- Volatilidad excesiva  
- Señales contradictorias  

El bot NUNCA enviará señales peligrosas.

---

## 🟦 3.4 signal_engine.py  
**Rol:** Generar señales finales combinando estrategia + riesgo + whale detector.

### Flujo:
1. Recibe pre-señal de `strategy.py`.  
2. Valida riesgo con `risk_manager.py`.  
3. Ajusta parámetros según volatilidad y ballenas.  
4. Produce señal final lista para enviar.

### Formato de señal:
```
{
  "pair": "SOL/USDT",
  "direction": "LONG",
  "entry": 132.40,
  "stop_loss": 128.90,
  "take_profit": 138.10,
  "confidence": 0.62,
  "reason": "Volumen x4 + EMA20 ruptura"
}
```

---

## 🟦 3.5 whale_detector.py  
**Rol:** Detectar actividad anómala en el mercado.

### Detecta:
- Volumen xN  
- Trades gigantes  
- Squeezes  
- Stop hunts  
- Muro de órdenes  
- Movimientos bruscos en segundos  

### Funciones principales:
- `detect_volume_spike(volume, avg_volume)`  
- `detect_large_trades(trades)`  
- `detect_fast_movement(candles)`  
- `detect_liquidations(data)`  

Al detectar anomalías, genera etiquetas como:

```
"whale_alert": true
"whale_reason": "Trade 1.8M USDT detectado"
```

---

## 🟦 3.6 position_manager.py (Futuro: versión 2.0)  
**Rol:** Administración de posiciones cuando el bot opere automáticamente.

- Abrir órdenes  
- Cerrar órdenes  
- Mover stop-loss  
- Trailing stop  
- Manejo de estado  

Aún no se implementa, pero queda definido.

---

## 🟦 3.7 utils.py  
Funciones auxiliares:

- Normalización de datos  
- Fechas, timestamps  
- Logs formateados  
- Cálculos repetitivos  

---

# 4. INTEGRACIÓN ENTRE MÓDULOS

```
WebSocket → indicators.py → strategy.py → whale_detector.py → risk_manager.py → signal_engine.py → DB → Web Panel / Telegram
```

Cada módulo es independiente y testeable.

---

# 5. PRINCIPIOS DE DISEÑO

- Desacoplamiento total  
- Código limpio  
- Funciones pequeñas  
- Documentación interna  
- Extensible para IA futura  
- Preparado para backtesting  

---

# 6. ESTADO DEL DOCUMENTO
✔ Módulos CORE definidos  
➡ Listo para crear Documento 04 — Estrategia Base

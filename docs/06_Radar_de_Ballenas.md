# 📄 06_Radar_de_Ballenas.md
**BOT DE TRADING CUANTITATIVO — RADAR DE BALLENAS (WHale & Volume Detector)**  
Versión: 1.0  
Autor: José Miguel Noé Torres  

---

# 1. PROPÓSITO DEL DOCUMENTO
Definir el módulo responsable de detectar **movimientos anormales en el mercado**, tales como:

- Volumen repentino (spikes)  
- Trades gigantes de ballenas  
- Movimientos bruscos del precio  
- Squeezes (liquidaciones masivas)  
- Stop hunts (barridos de liquidez)  
- Manipulación en orderbook  

Este módulo es crítico para evitar operaciones peligrosas y para identificar oportunidades que solo ocurren cuando **los actores grandes mueven el mercado**.

---

# 2. OBJETIVO DEL RADAR DE BALLENAS

El radar debe:

1. Detectar actividades inusuales en milisegundos.  
2. Alertar al motor de señales cuando existan condiciones extremas.  
3. Evitar operar contra ballenas.  
4. Identificar tendencias fuertes y rupturas genuinas.  

Si se activa una alerta, el bot debe:

- Rechazar señales de riesgo.  
- Etiquetar señales como “ballena detectada”.  
- Activar modo defensivo (según parámetros del riesgo).  

---

# 3. FUENTES DE DATOS UTILIZADAS

El radar usará información del **WebSocket de Binance**, que entrega:

### ✔ Trades ejecutados  
- tamaño  
- precio  
- agresor (buyer/seller)

### ✔ Orderbook (Depth)  
- muros de compra/venta  
- liquidez removida instantáneamente  

### ✔ Velas en tiempo real  
- cambios bruscos  
- mechas largas (stop hunts)  

### ✔ Volumen  
- comparación contra promedio histórico  

---

# 4. TIPOS DE EVENTOS QUE DETECTA

---

## 🟦 4.1 Volumen anómalo (Volume Spike)
Cuando el volumen de la vela actual es:

```
volumen_actual > volumen_promedio_20_velas * umbral
```

Ejemplo de umbral recomendado: **x3**

Genera alerta:
```
"volumen_spike": true
"factor": 3.2
```

---

## 🟦 4.2 Trades gigantes (Whale Trades)
Un trade es considerado de ballena si supera un umbral configurable:

```
trade.size > whale_min_usdt   # Ej: 250,000 USDT
```

Alerta:
```
"whale_trade_detected": true
"trade_value": 820000
"side": "SELL"
```

---

## 🟦 4.3 Movimiento brusco del precio
Se compara el cambio en segundos:

```
si abs(variacion_5s) > 0.4%
```

Alerta:
```
"fast_move": true
```

---

## 🟦 4.4 Squeezes (Liquidaciones masivas)
Si detecta:

- movimiento violento  
- volumen creciente  
- mecha larga contra operadores apalancados  

Alerta:
```
"squeeze_detected": true
```

---

## 🟦 4.5 Stop Hunts (Barrido de liquidez)
Se identifica una mecha larga que:

- rompe mínimos/máximos locales  
- y vuelve rápidamente al rango  

Alerta:
```
"stop_hunt": true
```

---

## 🟦 4.6 Manipulación de orderbook
Se detecta cuando:

- un muro gigante aparece y desaparece  
- compras o ventas masivas se retiran instantáneamente  

Alerta:
```
"spoofing_detected": true
```

---

# 5. FORMATO DE ALERTA GENERAL

```
{
  "pair": "BTC/USDT",
  "whale_trade": true,
  "large_trade_value": 1_200_000,
  "volume_spike": true,
  "volume_factor": 4.1,
  "fast_move": false,
  "stop_hunt": false,
  "squeeze_detected": true,
  "timestamp": 1736543200,
  "severity": "high",
  "reason": "Trade 1.2M + volumen x4"
}
```

---

# 6. LÓGICA INTERNA DEL MÓDULO

### Funciones previstas en `whale_detector.py`:

```
detect_volume_spike()
detect_large_trades()
detect_fast_price_movement()
detect_stop_hunt()
detect_squeeze()
detect_orderbook_manipulation()
```

Cada función devuelve:
- valor booleano  
- métricas asociadas  
- severidad del evento  

---

# 7. INTEGRACIÓN CON OTROS MÓDULOS

### ✔ Con `strategy.py`
- Si hay ballena en contra → INVALIDAR entrada  

### ✔ Con `risk_manager.py`
- Si severidad es "high" → bloquear trades por X minutos  

### ✔ Con `signal_engine.py`
- Señales llevan etiqueta: `"whale_alert": true`  

### ✔ Con el panel web
- Mostrar eventos visualmente  
- Alertas en tiempo real  

---

# 8. PARÁMETROS CONFIGURABLES

Archivo sugerido: `configs/whales.json`

```
{
  "volume_factor_threshold": 3.0,
  "whale_trade_min_usdt": 200000,
  "fast_move_threshold_pct": 0.004,
  "squeeze_min_factor": 1.8,
  "stop_hunt_wick_ratio": 2.0,
  "orderbook_wall_threshold": 500000
}
```

---

# 9. LOG DE EVENTOS

Cada evento se guarda en:

```
/logs/whales/fecha.log
```

Formato:

```
[2025-01-11 22:40] BTC/USDT | VOLUMEN x4.1 | TRADE 820k SELL | ALERTA HIGH
```

---

# 10. OBJETIVOS DEL MÓDULO

1. Evitar operar contra actores grandes.  
2. Detectar oportunidades reales (rupturas fuertes).  
3. Identificar mercado manipulado rápidamente.  
4. Aumentar precisión del bot.  
5. Proteger el capital en condiciones peligrosas.  

---

# 11. ESTADO DEL DOCUMENTO
✔ Radar de ballenas documentado  
➡ Listo para Documento 07 — Datos & APIs

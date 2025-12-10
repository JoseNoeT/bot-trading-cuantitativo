# 📄 07_Datos_y_APIs.md
**BOT DE TRADING CUANTITATIVO — DATOS & APIs (REST + WebSocket Binance)**  
Versión: 1.0  
Autor: José Miguel Noé Torres  

---

# 1. PROPÓSITO DEL DOCUMENTO
Este documento define cómo el bot obtiene **datos del mercado** usando las APIs oficiales de Binance, tanto:

- **REST API** → Datos históricos, precios puntuales  
- **WebSocket API** → Datos en tiempo real (trades, orderbook, velas, volumen)

El objetivo es estandarizar la forma en que el bot obtiene, procesa y entrega los datos al sistema CORE.

---

# 2. TIPOS DE DATOS NECESARIOS PARA EL BOT

El bot requiere 4 grandes categorías de datos:

### 🟦 2.1 Velas (Klines)
- OHLC (Open, High, Low, Close)  
- Volumen  
- Timestamp  
- Duración configurable (1m, 5m, 15m, etc.)

### 🟩 2.2 Order Book (profundidad)
- Mejores 20 niveles de compra  
- Mejores 20 niveles de venta  
- Cambios instantáneos (liquidez removida)

Necesario para detectar manipulación.

---

### 🟧 2.3 Trades ejecutados
- Precio  
- Cantidad  
- Total en USDT  
- Order aggressor (BUY/SELL)

Necesario para detectar ballenas.

---

### 🟨 2.4 Información del mercado
- Precio actual  
- Volumen 24h  
- Alta y baja del día  
- Funding rate (si operara futuros)

---

# 3. API REST DE BINANCE — ENDPOINTS UTILIZADOS

Archivo recomendado:  
`data/binance_api.py`

---

## 🟦 3.1 Klines (velas)
```
GET /api/v3/klines
```

Parámetros:
- symbol  
- interval  
- limit  

Ejemplo:
```
/api/v3/klines?symbol=BTCUSDT&interval=5m&limit=200
```

---

## 🟩 3.2 Precio actual
```
GET /api/v3/ticker/price
```

---

## 🟧 3.3 Volumen y estadísticas 24h
```
GET /api/v3/ticker/24hr
```

---

## 🟨 3.4 Order Book (datos puntuales)
```
GET /api/v3/depth
```

Parámetros:
- limit (5, 10, 20, 100, 500)

---

## 🟥 3.5 Manejo de límites
Binance impone límites por minuto.  
El bot debe:

- cachear datos  
- evitar llamadas excesivas  
- usar WebSocket para tiempo real  

---

# 4. API WEBSOCKET — DATOS EN TIEMPO REAL

Archivo recomendado:  
`data/websocket_stream.py`

---

## 🟦 4.1 WebSocket de velas (kline stream)

URL:
```
wss://stream.binance.com:9443/ws/<symbol>@kline_<interval>
```

Ejemplo:
```
wss://stream.binance.com:9443/ws/btcusdt@kline_1m
```

Datos recibidos:
```
t → open time
o → open price
h → high
l → low
c → close
v → volume
```

---

## 🟩 4.2 WebSocket de trades

URL:
```
wss://stream.binance.com:9443/ws/<symbol>@trade
```

Datos recibidos:
- precio  
- cantidad  
- buyer/seller  
- trade_id  

Usado en el radar de ballenas.

---

## 🟧 4.3 WebSocket del orderbook (Depth Stream)

URL:
```
wss://stream.binance.com:9443/ws/<symbol>@depth20@100ms
```

Esto permite:

- detectar muros de compra/venta  
- detectar removiones instantáneas → spoofing  
- identificar liquidez real  

---

# 5. NORMALIZACIÓN DE DATOS

Todos los datos pasan por un módulo estandarizador, para que el resto del bot reciba estructuras limpias.

Ejemplo formato vela:
```
{
  "timestamp": 1736543200,
  "open": 132.40,
  "high": 133.10,
  "low": 131.80,
  "close": 132.90,
  "volume": 450000
}
```

Ejemplo trade:
```
{
  "price": 132.91,
  "qty": 820,
  "value": 108000,
  "side": "SELL"
}
```

---

# 6. FALLAS Y RECONECTORES AUTOMÁTICOS

El bot debe reconectar WebSockets automáticamente si ocurre:

- desconexión  
- error de red  
- timeout  

Pseudocódigo:
```
while True:
    try:
        conectar websocket
        escuchar mensajes
    except:
        esperar 3s
        reconectar
```

---

# 7. MANEJO DE EXCEPCIONES

Errores comunes:
- API limit exceeded  
- Bad response format  
- No internet  
- Datos nulos  

Cada error debe loguearse en:

```
/logs/api/fecha.log
```

---

# 8. ALMACENAMIENTO DE DATOS

### Caché temporal
- Diccionarios en memoria  
- Últimas velas  
- Últimos trades  
- Último estado del orderbook  

### Persistencia opcional
- SQLite  
- PostgreSQL  

---

# 9. FLUJO DE DATOS COMPLETO

```
REST API → obtener velas históricas
WS → recibir velas nuevas en tiempo real
WS → recibir trades
WS → recibir profundidad
NORMALIZAR → pasar a módulos CORE
CORE → generar señales
SEÑALES → panel web / Telegram / logs
```

---

# 10. PARÁMETROS CONFIGURABLES

Archivo recomendado: `configs/data.json`

```
{
  "symbols": ["BTCUSDT", "ETHUSDT", "SOLUSDT"],
  "kline_interval": "1m",
  "kline_limit": 200,
  "websocket_reconnect_delay": 3
}
```

---

# 11. OBJETIVOS GLOBALES DEL MÓDULO

- Obtener datos confiables  
- Reducir latencia  
- Evitar duplicación  
- Manejo limpio de errores  
- Compatibilidad con backtesting  
- Preparado para multi-moneda  

---

# 12. ESTADO DEL DOCUMENTO
✔ Datos & APIs definidos  
➡ Listo para Documento 08 — Backtesting

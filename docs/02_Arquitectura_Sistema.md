# 📄 02_Arquitectura_Sistema.md
**BOT DE TRADING CUANTITATIVO — ARQUITECTURA DEL SISTEMA**  
Versión: 1.0  
Autor: José Miguel Noé Torres  

---

# 1. PROPÓSITO DEL DOCUMENTO
Establecer la **arquitectura técnica completa** del bot de trading cuantitativo, definiendo:

- Componentes del sistema  
- Flujo de datos  
- Comunicación interna entre módulos  
- Cómo se integra el panel web  
- Cómo se ejecuta el bot en local y en servidor  

Este documento sirve como guía principal para desarrollo, colaboración con Copilot y escalabilidad futura.

---

# 2. DISEÑO GENERAL DE ALTO NIVEL

El sistema se divide en **tres capas principales**:

### 🟦 **Capa 1 — CORE (Lógica del Bot)**
Responsable de análisis, estrategias y riesgo.

### 🟩 Capa 2 — DATA (Conexión a Binance)
Se encarga de API REST, WebSocket y almacenamiento temporal.

### 🟧 Capa 3 — WEB PANEL (Interfaz)
Permite visualizar señales, métricas y estado del bot desde un navegador.

---

# 3. DIAGRAMA DE ARQUITECTURA (ALTO NIVEL)

```
                ┌────────────────────┐
                │     Binance API     │
                │ REST + WebSocket    │
                └─────────┬──────────┘
                          │
                ┌─────────▼──────────┐
                │     DATA LAYER      │
                │ binance_api.py      │
                │ websocket_stream.py │
                └─────────┬──────────┘
                          │
        ┌─────────────────┼──────────────────┐
        │                 │                  │
┌───────▼──────┐   ┌──────▼──────┐    ┌──────▼────────┐
│ STRATEGY      │   │ RISK MANAGER │    │ WHALE DETECTOR │
│ (core/)       │   │ (core/)      │    │ (core/)         │
└───────┬──────┘   └──────┬──────┘    └──────────┬──────┘
        │                 │                      │
        └────────────┬────┴─────────────┬────────┘
                     │                  │
             ┌───────▼──────┐     ┌─────▼─────────┐
             │ SIGNAL ENGINE │     │ LOGGER SERVICE │
             └───────┬──────┘     └─────┬─────────┘
                     │                  │
            ┌────────▼──────────────┐
            │    DATABASE / CACHE   │
            │ (SQLite / PostgreSQL) │
            └────────┬──────────────┘
                     │
               ┌─────▼────┐
               │  WEB API  │  Flask / FastAPI
               └─────┬────┘
                     │
               ┌─────▼─────────────┐
               │   WEB PANEL       │
               │ (HTML/React)      │
               └────────────────────┘
```

---

# 4. DETALLE DE CADA MÓDULO

## 🟦 **4.1 CORE (Lógica nuclear del bot)**

### ✔ `strategy.py`
Implementa la estrategia base:
- Tendencia  
- Volatilidad  
- Breakouts  
- Cálculo de SL/TP  
- Señales LONG/SHORT  

### ✔ `risk_manager.py`
Controla:
- Tamaño de posición  
- Máxima pérdida diaria  
- Bloqueos de seguridad  
- Stop Loss obligatorio  

### ✔ `whale_detector.py`
Detecta:
- Volumen anómalo  
- Movimientos bruscos  
- Trades grandes (ballenas)  
- Liquidaciones  

### ✔ `indicators.py`
Cálculo de:
- EMA, SMA  
- RSI  
- MACD  
- ATR  
- Estructura de precio  

---

# 🟩 **4.2 DATA LAYER (Conexión a Binance)**

### ✔ `binance_api.py`
Funciones clave:
- Obtener velas históricas  
- Obtener precios  
- Obtener volumen  
- Consultar estado de cuenta (futuros o spot)  

### ✔ `websocket_stream.py`
Recibe:
- Trades en tiempo real  
- Orderbook  
- Velas actualizadas  
- Movimientos bruscos del mercado  

Permite al bot reaccionar **en milisegundos**.

---

# 🟧 **4.3 WEB PANEL**
Panel accesible desde el navegador del notebook:

### ✔ Backend Web (FastAPI / Flask)
Expone rutas:

- `/signals`
- `/metrics`
- `/status`
- `/settings`
- `/logs`

### ✔ Frontend (HTML/Tailwind o React)
Visualizaciones:

- Señales actuales  
- Estado del bot  
- Logs  
- Movimientos de ballenas  
- Estadísticas  

---

# 5. BASE DE DATOS

### ✔ SQLite (versión local)
Ideal para:
- Logs  
- Señales  
- Configuración  

### ✔ PostgreSQL (versión nube)
Para:
- Escalabilidad  
- Dashboard avanzado  

---

# 6. FLUJO COMPLETO DE EJECUCIÓN

1. WebSocket recibe datos del mercado.  
2. DATA LAYER limpia y normaliza los datos.  
3. CORE (estrategia + riesgo + ballenas) analiza.  
4. ENGINE genera señal.  
5. Señal se guarda en DB.  
6. WEB PANEL la muestra en tiempo real.  
7. ALERT TELEGRAM envía notificación.  
8. Usuario actúa manualmente.  
   (*Automatización vendrá en versión futura.*)

---

# 7. EJECUCIÓN DEL BOT

### LOCAL (notebook)
```
python main.py
python web/api.py
```

### NUBE (futuro)
- Docker  
- Railway / Render  
- VPS Ubuntu  

---

# 8. OBJETIVOS DE ARQUITECTURA

- Escalable  
- Módulos separados  
- Fácil mantenimiento  
- Código limpio para colaboración con Copilot  
- Seguridad y control de riesgo integrados  

---

# 9. ESTADO DEL DOCUMENTO
✔ Documento aprobado  
➡ Listo para construir el Documento 03 — Módulos Core


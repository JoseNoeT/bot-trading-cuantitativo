# Bot de Trading Cuantitativo

Sistema experimental desarrollado en Python para analizar datos de mercado, generar señales estructuradas y aplicar reglas de gestión de riesgo sobre estrategias de trading cuantitativo.

> **Estado:** núcleo cuantitativo implementado y probado. Las integraciones en tiempo real, API web y alertas externas continúan en desarrollo.

---

## 1. Descripción general

El proyecto busca construir una arquitectura modular para analizar mercados de criptomonedas y separar claramente la lógica de indicadores, estrategia, riesgo, detección de actividad anómala e integraciones externas.

La versión actual implementa el núcleo de análisis y dispone de pruebas automatizadas. Los conectores con Binance y las capas de exposición web todavía se encuentran como estructura base y no deben considerarse funcionalidades terminadas.

---

## 2. Objetivos del sistema

| Objetivo | Estado |
|----------|--------|
| Indicadores técnicos | Implementado |
| Detección de tendencia | Implementado |
| Validación de volumen | Implementado |
| Generación de pre-señales LONG/SHORT | Implementado |
| Gestión de riesgo | Implementado |
| Construcción de SL/TP | Implementado |
| Tamaño de posición | Implementado |
| Detección de actividad anómala | Implementado |
| Ensamblado de señal final | Implementado |
| Pruebas automatizadas | Implementado |
| Integración REST con Binance | Pendiente |
| Streams WebSocket | Pendiente |
| API web | Pendiente |
| Alertas externas | Pendiente |

---

## 3. Tecnologías

| Componente | Tecnología |
|------------|------------|
| Lenguaje | Python |
| Exchange objetivo | Binance |
| Comunicación planificada | REST / WebSocket |
| API web planificada | FastAPI |
| Pruebas | pytest |
| Integración continua | GitHub Actions |
| Configuración | JSON |

Dependencias declaradas actualmente:

- python-binance
- websockets
- fastapi
- uvicorn

---

## 4. Arquitectura

```text
bot-trading-cuantitativo/
├── .github/
│   └── workflows/
│       └── tests.yml
├── bot/
│   ├── configs/
│   │   ├── data.json
│   │   ├── risk.json
│   │   └── whales.json
│   ├── core/
│   │   ├── indicators.py
│   │   ├── risk_manager.py
│   │   ├── signal_engine.py
│   │   ├── strategy.py
│   │   ├── utils.py
│   │   └── whale_detector.py
│   ├── data/
│   │   ├── binance_api.py
│   │   └── websocket_stream.py
│   ├── services/
│   │   ├── alert_telegram.py
│   │   └── logger.py
│   ├── tests/
│   └── web/
│       └── api.py
├── docs/
├── main.py
├── requirements.txt
└── README.md
```

La arquitectura separa el núcleo cuantitativo de las futuras integraciones externas. Esto permite probar la lógica de estrategia y riesgo sin depender de conexiones en tiempo real.

---

## 5. Módulos implementados

### Indicadores técnicos

`bot/core/indicators.py` implementa funciones para:

- SMA;
- EMA;
- ATR;
- RSI;
- MACD;
- volatilidad.

Las funciones realizan validación de entradas y no dependen de librerías externas de análisis técnico.

### Estrategia

`bot/core/strategy.py` contiene la lógica para:

- detectar tendencia mediante EMA20 y EMA50;
- validar volumen;
- calcular ATR;
- generar pre-señales LONG o SHORT;
- descartar escenarios sin condiciones suficientes.

### Gestión de riesgo

`bot/core/risk_manager.py` implementa:

- cálculo de tamaño de posición;
- validación de Stop Loss y Take Profit;
- ratio riesgo/beneficio;
- control de pérdida diaria;
- límite de operaciones;
- filtro de volatilidad;
- construcción de una señal validada por riesgo.

### Motor de señales

`bot/core/signal_engine.py` combina:

1. estrategia;
2. análisis de actividad anómala;
3. filtros de riesgo;
4. cálculo de SL/TP;
5. tamaño de posición;
6. puntuación heurística de confianza.

El resultado es una señal estructurada o `None` cuando las condiciones no superan los filtros.

### Detección de actividad anómala

`bot/core/whale_detector.py` contiene detectores experimentales basados en velas para:

- volumen extremo;
- movimientos rápidos;
- cuerpos de vela anómalos;
- mechas largas;
- compresión y expansión;
- clasificación de severidad.

Estos detectores son heurísticos y no identifican por sí solos operaciones reales de grandes participantes del mercado.

---

## 6. Componentes pendientes

Los siguientes archivos existen como estructura inicial, pero todavía no representan integraciones completas:

| Componente | Archivo | Estado |
|------------|---------|--------|
| Binance REST | `bot/data/binance_api.py` | Placeholder |
| Binance WebSocket | `bot/data/websocket_stream.py` | Placeholder |
| API web | `bot/web/api.py` | Placeholder |
| Alertas Telegram | `bot/services/alert_telegram.py` | Base pendiente de integración |

Por esta razón, la versión actual debe entenderse como un **motor cuantitativo en desarrollo**, no como un bot autónomo operando en producción.

---

## 7. Pruebas y calidad

El repositorio incluye pruebas automatizadas para los principales componentes del núcleo:

- indicadores;
- estrategia;
- gestión de riesgo;
- motor de señales;
- detector de actividad anómala.

La carpeta de pruebas se encuentra en:

```text
bot/tests/
```

El workflow `.github/workflows/tests.yml` ejecuta la suite con `pytest` mediante GitHub Actions para Python 3.10 y 3.11.

Ejecución local:

```bash
pytest -q
```

---

## 8. Instalación local

Clonar el repositorio:

```bash
git clone https://github.com/JoseNoeT/bot-trading-cuantitativo.git
cd bot-trading-cuantitativo
```

Crear un entorno virtual:

```bash
python -m venv .venv
```

Activar en Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

Activar en Linux/macOS:

```bash
source .venv/bin/activate
```

Instalar dependencias:

```bash
pip install -r requirements.txt
pip install pytest
```

Ejecutar las pruebas:

```bash
pytest -q
```

---

## 9. Documentación técnica

La carpeta `docs/` contiene la documentación de diseño original:

1. `01_Idea_Principal_Base.md`
2. `02_Arquitectura_Sistema.md`
3. `03_Modulos_Core.md`
4. `04_Estrategia_Base.md`
5. `05_Gestion_de_Riesgo.md`
6. `06_Radar_de_Ballenas.md`
7. `07_Datos_y_APIs.md`
8. `08_Fases_de_Desarrollo.md`

Parte de esta documentación describe la arquitectura objetivo y, por tanto, puede incluir componentes todavía no implementados.

---

## 10. Seguridad

- No almacenar claves de Binance directamente en el código.
- Utilizar variables de entorno para futuras credenciales.
- Mantener separadas las credenciales de prueba y producción.
- No utilizar el proyecto con capital real sin validación, backtesting y controles adicionales.

---

## 11. Estado actual

### Implementado

- Núcleo de indicadores.
- Estrategia basada en tendencia, volumen y ATR.
- Gestión de riesgo.
- Motor de señales.
- Detección heurística de actividad anómala.
- Pruebas automatizadas.
- CI con GitHub Actions.

### Pendiente

- Consumo real de Binance REST.
- Streams WebSocket.
- Persistencia de datos.
- Backtesting completo.
- API web funcional.
- Panel de visualización.
- Sistema de alertas.
- Validación integral con datos reales.
- Preparación para despliegue.

### Deuda técnica detectada

- Existen archivos `__pycache__` y `.pyc` versionados que deben retirarse del repositorio.
- Algunos módulos conservan funciones `placeholder()` heredadas de fases anteriores.
- La documentación de `docs/` requiere una revisión de codificación UTF-8 y sincronización con el estado actual.
- El punto de entrada `main.py` todavía corresponde a un scaffold inicial.

---

## 12. Alcance

Este repositorio es un proyecto de aprendizaje y experimentación técnica. No constituye asesoría financiera ni un sistema de trading listo para producción.

El objetivo técnico es desarrollar y validar de forma progresiva una arquitectura modular para análisis cuantitativo, gestión de riesgo e integración con datos de mercado.

---

## Autor

**José Noé Torres**

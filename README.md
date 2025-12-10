# 🧠 Bot de Trading Cuantitativo — Proyecto Base

Autor: **José Miguel Noé Torres**  
Versión: 1.0 (Diseño de arquitectura y guía de desarrollo)

---

## 📌 Descripción General

Este repositorio contiene el código y la documentación para construir un **bot de trading cuantitativo** que:

- Analiza el mercado cripto en tiempo real (Binance).
- Genera **señales de trading estructuradas** (entrada, SL, TP, confianza).
- Incluye **gestión de riesgo estricta** (pérdida diaria máxima, tamaño de posición, filtros de volatilidad).
- Integra un **Radar de Ballenas** (volumen anómalo, trades gigantes, manipulación).
- Expone la información a través de un **panel web** accesible desde el notebook.
- Envía **alertas** (Telegram / otros) en fases posteriores.

---

## 🧱 Estado Actual

En esta primera versión el foco está en:

- Diseño de arquitectura.
- Definición de módulos principales.
- Guía de desarrollo por fases.
- Documentación funcional y técnica en `/docs`.

El código Python se irá implementando fase por fase siguiendo esta guía.

---

## 📂 Estructura Inicial del Proyecto

Sugerencia de estructura de carpetas para este repositorio:

```bash
bot-trading-cuantitativo/
├── docs/
│   ├── 01_Idea_Principal_Base.md
│   ├── 02_Arquitectura_Sistema.md
│   ├── 03_Modulos_Core.md
│   ├── 04_Estrategia_Base.md
│   ├── 05_Gestion_de_Riesgo.md
│   ├── 06_Radar_de_Ballenas.md
│   ├── 07_Datos_y_APIs.md
│   ├── 08_Fases_de_Desarrollo.md
│   └── README_docs.md (opcional)
├── bot/
│   ├── core/
│   ├── data/
│   ├── services/
│   ├── web/
│   ├── configs/
│   └── __init__.py
├── tests/
├── logs/
├── .gitignore
├── README.md   ← (este archivo)
└── requirements.txt
```

---

## 📚 Documentación Oficial del Proyecto

Toda la guía de desarrollo vive en la carpeta `/docs`.

- `01_Idea_Principal_Base.md` → Visión y objetivo del bot.  
- `02_Arquitectura_Sistema.md` → Arquitectura completa (Core, Data, Web).  
- `03_Modulos_Core.md` → Definición de `strategy`, `risk_manager`, `signal_engine`, etc.  
- `04_Estrategia_Base.md` → Estrategia cuantitativa inicial (tendencia + volumen + ATR).  
- `05_Gestion_de_Riesgo.md` → Reglas de riesgo (SL, TP, pérdidas diarias, filtros).  
- `06_Radar_de_Ballenas.md` → Diseño del módulo Whale & Volume Detector.  
- `07_Datos_y_APIs.md` → Uso de REST + WebSocket de Binance.  
- `08_Fases_de_Desarrollo.md` → Roadmap oficial de desarrollo.

> ✅ Con estos 8 documentos, Copilot y el autor tienen una guía completa para construir el bot paso a paso.

---

## 🚀 Guía Rápida para Iniciar el Desarrollo

1. **Crear el repositorio en GitHub**  
   Nombre sugerido (puedes cambiarlo):
   - `bot-trading-cuantitativo`
   - `quant-crypto-bot`
   - `binance-quant-bot`

2. **Clonar el repositorio en el notebook**
   ```bash
   git clone <URL_DEL_REPO>
   cd <NOMBRE_DEL_REPO>
   ```

3. **Crear la estructura de carpetas inicial**
   ```bash
   mkdir -p docs bot/core bot/data bot/services bot/web bot/configs tests logs
   ```

4. **Copiar los archivos .md de documentación en `/docs`**
   - Guardar aquí todos los documentos generados (01 al 08).

5. **Crear entorno virtual e instalar dependencias (más adelante)**
   ```bash
   python -m venv .venv
   source .venv/Scripts/activate  # Windows
   # o source .venv/bin/activate  # Linux/Mac

   pip install -r requirements.txt
   ```

   > Por ahora, `requirements.txt` puede empezar vacío o con dependencias básicas como:
   > `python-binance`, `websockets`, `fastapi`/`flask`, `uvicorn`, etc. (se definirán en la fase de implementación).

---

## 🧠 Filosofía del Proyecto

- **Primero la lógica, luego el código.**
- Todo debe ser:
  - Medible  
  - Backtesteable  
  - Reproducible  
  - Controlado en riesgo  

No se busca crear un bot de “señales mágicas”, sino un sistema cuantitativo serio.

---

## 🗺️ Roadmap Resumido

Las fases detalladas están en `docs/08_Fases_de_Desarrollo.md`, pero el resumen es:

1. Arquitectura y documentos  
2. Módulos Core  
3. Data Layer (APIs)  
4. Estrategia Base  
5. Gestión de Riesgo  
6. Radar de Ballenas  
7. Backtesting  
8. Panel Web  
9. Alertas  
10. Producción

---

## 🤝 Colaboración con Copilot

- Usar los documentos en `/docs` como **fuente de verdad**.  
- Pedir a Copilot implementar cada módulo respetando:
  - nombres de archivos  
  - funciones descritas  
  - responsabilidades definidas  

Ejemplo de prompt para Copilot:

> “Basado en `docs/03_Modulos_Core.md`, implementa el archivo `bot/core/indicators.py` con funciones para EMA, ATR, RSI y MACD, usando nombres de variables claros y tipos de datos limpios.”

---

## 🔒 Notas sobre Seguridad

- Nunca exponer claves de API de Binance en el código.  
- Usar variables de entorno o un archivo `.env` (no subirlo a Git).  
- Probar primero en modo paper trading o con montos pequeños.

---

## 📎 Próximos Pasos

1. Crear el repositorio en GitHub.  
2. Subir este `README.md`.  
3. Crear la carpeta `/docs` y agregar los 8 documentos.  
4. Definir `requirements.txt`.  
5. Empezar con la implementación de `bot/core/indicators.py`.


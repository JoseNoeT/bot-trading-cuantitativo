# 📄 04_Estrategia_Base.md
**BOT DE TRADING CUANTITATIVO — ESTRATEGIA BASE (VERSIÓN 1.0)**  
Autor: José Miguel Noé Torres  

---

# 1. PROPÓSITO DEL DOCUMENTO
Definir la **estrategia cuantitativa principal** utilizada por el bot para producir señales de trading en su **versión 1.0**.  
Esta estrategia debe ser:

- Simple  
- Basada en datos  
- Razonable estadísticamente  
- Fácil de backtestear  
- Segura para operar en real más adelante  

No pretende ser perfecta: es la **columna vertebral inicial** del sistema, sobre la cual se agregarán mejoras y filtros avanzados.

---

# 2. ENFOQUE DE LA ESTRATEGIA BASE
La estrategia seleccionada para V1 es:

> **Tendencia + Volumen + Volatilidad Controlada**

Este enfoque combina:

1. **Dirección del mercado (tendencia clara)**
2. **Confirmación con volumen**
3. **Entrada precisa basada en retrocesos o rupturas**
4. **Stop Loss basado en volatilidad (ATR)**
5. **Take Profit con riesgo/beneficio fijo**

Es robusta, estable y no requiere predicciones.

---

# 3. COMPONENTES PRINCIPALES

### ✔ 3.1 Tendencia con EMAs
La tendencia se evalúa usando:

- **EMA20** (dirección rápida)
- **EMA50** (dirección media)
- **EMA200** (dirección de largo plazo)

Reglas:

- `EMA20 > EMA50` → tendencia alcista
- `EMA20 < EMA50` → tendencia bajista
- Separación amplia → fuerza de tendencia

---

### ✔ 3.2 Confirmación de Volumen
Se compara el volumen actual con el **volumen promedio de 20 velas**.

- Volumen actual > 1.5x del promedio → válido
- Volumen actual < promedio → señal ignorada

Previene entradas falsas.

---

### ✔ 3.3 Volatilidad con ATR
El **ATR (Average True Range)** determina:

- Tamaño del stop loss  
- Distancia mínima para validar entrada  
- Evitar mercados hiper volátiles  

Regla:

- Si `ATR > límite_max_volatilidad` → NO operar.

---

### ✔ 3.4 Condiciones de Entrada

#### 🟢 Entrada LONG (compra)
1. EMA20 cruza hacia arriba EMA50  
2. Precio retrocede sin romper EMA20 en cierre  
3. Volumen por encima de promedio  
4. No hay alerta de ballenas vendiendo en ese minuto  

**Entrada = cierre de la vela de confirmación**

---

#### 🔴 Entrada SHORT (venta)
1. EMA20 cruza hacia abajo EMA50  
2. Retroceso hacia EMA20 que falla  
3. Volumen fuerte en dirección bajista  
4. No hay alerta de ballenas comprando

---

### ✔ 3.5 Stop Loss (SL)
Basado en ATR:

```
SL = entry_price - (1.5 * ATR)   # para LONG
SL = entry_price + (1.5 * ATR)   # para SHORT
```

SL dinámico y adaptable al mercado.

---

### ✔ 3.6 Take Profit (TP)
Se define usando **riesgo/beneficio fijo**:

- Ratio recomendado: **1 : 2**
- TP = distancia SL * 2

Ejemplo:
- SL = 1.5%
- TP = 3%

---

# 4. FILTROS ADICIONALES

### ✔ 4.1 Filtro de estructura
Evita operar contra zonas fuertes.

### ✔ 4.2 Filtro de ballenas (del módulo whale_detector.py)
Ignorar señales si:

- Volumen gigante aparece en contra
- Hay manipulación evidente
- Movimientos muy rápidos en segundos

### ✔ 4.3 No operar en laterales
Mercado lateral = EMAs entrelazadas.

---

# 5. FORMATO FINAL DE SEÑAL (OUTPUT)

```
pair: SOL/USDT
direction: LONG
entry: 132.40
stop_loss: 128.90
take_profit: 138.10
confidence: 0.62
reason:
  - Tendencia alcista (EMA20>EMA50)
  - Volumen x2
  - ATR normal
  - Ruptura con retroceso saludable
```

---

# 6. FLUJO LÓGICO DE LA ESTRATEGIA

```
1. Recibir velas → indicadores.py
2. Calcular EMAs, volumen, ATR
3. Determinar tendencia
4. Validar volumen
5. Verificar volatilidad
6. Chequear actividad de ballenas
7. Encontrar setup de entrada
8. Calcular SL y TP
9. Pasar a risk_manager.py
10. Enviar a signal_engine.py → señal final
```

---

# 7. LIMITACIONES DE LA ESTRATEGIA
- No funciona bien en rangos laterales
- Depende de volatilidad estable
- Falsos retrocesos pueden ocurrir
- Noticias pueden invalidar cualquier señal

Por eso existe gestión de riesgo estricta.

---

# 8. OBJETIVOS DE ESTA ESTRATEGIA
- Ser simple y medible
- Ser fácil de backtestear
- Servir como base para mejoras futuras:
  - Breakouts avanzados
  - Machine Learning
  - Multi-activos dinámicos
  - Reversiones cuantitativas

---

# 9. ESTADO DEL DOCUMENTO
✔ Estrategia base definida  
➡ Listo para crear Documento 05 — Gestión de Riesgo

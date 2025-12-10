# 📄 05_Gestion_de_Riesgo.md
**BOT DE TRADING CUANTITATIVO — GESTIÓN DE RIESGO**  
Versión: 1.0  
Autor: José Miguel Noé Torres  

---

# 1. PROPÓSITO DEL DOCUMENTO
Definir las reglas de **gestión de riesgo** del bot, que son obligatorias y tienen prioridad sobre cualquier estrategia o señal.  
El objetivo principal es **proteger el capital**, limitar pérdidas y evitar comportamientos peligrosos del sistema.

> Un bot sin riesgo controlado se destruye solo.  
> Un bot con riesgo sólido puede sobrevivir y mejorar.

---

# 2. PRINCIPIOS FUNDAMENTALES
Toda decisión del bot debe cumplir estos principios:

1. **Nunca arriesgar más de lo permitido.**  
2. **Nunca abrir una operación sin Stop Loss.**  
3. **Nunca operar si el mercado está demasiado volátil.**  
4. **Nunca operar en contra de señales fuertes de ballenas.**  
5. **Nunca exceder pérdidas diarias máximas.**  
6. **Cerrar todo y bloquear si el riesgo se dispara.**

La prioridad es la seguridad, no la cantidad de señales.

---

# 3. COMPONENTES DE LA GESTIÓN DE RIESGO

Los módulos principales del riesgo son:

### ✔ 3.1 Control de posición (Position Sizing)
Determina cuánto capital usar en cada trade según:

- balance total  
- porcentaje de riesgo definido  
- distancia del Stop Loss (SL)  
- volatilidad del activo (ATR)  

**Fórmula base:**

```
riesgo_monetario = balance * riesgo_por_trade
posicion = riesgo_monetario / distancia_SL
```

Ejemplo:  
- Balance: 1,000 USDT  
- Riesgo por trade: 1% → 10 USDT  
- Distancia SL: 0.5%  
- Tamaño posición = 10 / 0.005 = 2,000 USDT (apalancado o spot)

---

### ✔ 3.2 Stop Loss obligatorio
Cada operación debe tener SL dinámico basado en ATR:

```
SL = entry ± (1.5 * ATR)
```

Sin SL → la señal se rechaza automáticamente.

---

### ✔ 3.3 Take Profit racional
- Ratio riesgo/beneficio 1:2  
- TP = distancia SL * 2  
- Evita TP irracionales

---

### ✔ 3.4 Límite de pérdidas diarias (Daily Loss Limit)

Protección absoluta:

```
si perdidas_dia >= max_perdida_dia:
    bloquear_trading()
```

Ejemplo recomendado:
- Máxima pérdida diaria: **3% del capital**
- Si se pierde 3% → se apaga el bot por ese día.

---

### ✔ 3.5 Límite de operaciones por día
Evita sobreoperar en días malos.

Regla:

```
max_trades_por_dia = 5
```

Si el bot llega al límite, suspende nuevas señales.

---

### ✔ 3.6 Filtro de volatilidad extrema
Evita operar cuando el mercado es caótico.

Ejemplo:

```
si ATR > 2.5% del precio:
    ignorar señal
```

Evita perder en velas violentas.

---

### ✔ 3.7 Filtro de ballenas (Whale Risk Filter)
Si se detecta:

- Volumen x5  
- Trade gigante en contra  
- Stop hunt evidente  
- Manipulación brusca  

Entonces:

```
si whale_detector.alerta:
    rechazar señal
```

El bot no pelea contra ballenas.

---

### ✔ 3.8 Bloqueo de emergencia
Cuando se detecta una condición peligrosa:

- pérdida diaria superada  
- entorno hipervolátil  
- API fallando  
- señales contradictorias  
- conexión inestable  

Entonces:

```
estado_bot = "bloqueado"
```

Y solo puede reiniciarse manualmente.

---

# 4. WORKFLOW DE RIESGO

```
1. Estrategia genera pre-señal
2. Risk Manager revisa:
      - tamaño de posición
      - SL válido
      - TP válido
      - ratio 1:2
      - ATR / volatilidad
      - pérdidas acumuladas
      - volumen anómalo
      - actividad de ballenas
3. Si falla → señal rechazada
4. Si pasa → enviar a signal_engine
```

---

# 5. PARÁMETROS CONFIGURABLES

Archivo sugerido: `configs/risk.json`

```
{
  "risk_per_trade": 0.01,
  "max_daily_loss": 0.03,
  "max_trades_per_day": 5,
  "min_volume_factor": 1.5,
  "max_volatility_pct": 0.025
}
```

Todos los valores podrán configurarse desde el panel web.

---

# 6. VALIDACIÓN Y TESTING

Tests unitarios obligatorios:

- no abrir operación con SL inválido  
- no abrir operación con volatilidad extrema  
- bloquear bot tras pérdida diaria  
- rechazar señal con ballenas en contra  
- validar tamaño de posición correctamente  
- validar ratio SL/TP correctamente  

---

# 7. OBJETIVO FINAL DEL RIESGO

1. Proteger el capital  
2. Asegurar operaciones lógicas  
3. Evitar destrucción de cuenta  
4. Mantener al bot disciplinado  
5. Controlar emociones del operador humano  

---

# 8. ESTADO DEL DOCUMENTO
✔ Gestión de riesgo definida  
➡ Listo para Documento 06 — Radar de Ballenas

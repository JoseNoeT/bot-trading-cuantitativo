"use strict";
// Presentation-only controller. Never connects to private accounts or sends real orders.
(function () {
  const form = document.getElementById("order-review-form");
  const result = document.getElementById("order-review-result");
  if (!form || !result) return;

  function el(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = String(text);
    return node;
  }
  function render(payload) {
    result.replaceChildren();
    result.classList.add("review-output");
    const header = el("div", "review-heading");
    const title = el("div", "", "Evaluación de " + payload.symbol);
    const badge = el("span", "review-badge", "ORDEN NO VERIFICADA");
    header.append(title, badge);
    result.append(header);

    const verdict = el("div", "review-verdict");
    verdict.append(el("strong", "", "Decisión: REVISAR / NO OPERAR"),
                   el("p", "", "El contexto es " + (payload.market_context === "MIXTO_O_SIN_CONFIRMACION"
                     ? "mixto, sin confirmación suficiente."
                     : String(payload.market_context || "no determinado") + ".")));
    result.append(verdict);

    const metrics = el("div", "review-metrics");
    const rows = [
      ["Precio límite", payload.limit_price + " USDT"],
      ["Último cierre 15m", payload.reference_close_15m + " USDT"],
      ["Distancia al límite", payload.distance_to_limit_pct + " %"],
      ["Cantidad", payload.quantity + " " + payload.symbol.replace("USDT", "")],
      ["Importe nominal", payload.nominal_usdt + " USDT"],
      ["Tipo", payload.side === "BUY" ? "COMPRA" : "VENTA"]
    ];
    for (const [label, value] of rows) {
      const cell = el("div", "review-metric");
      cell.append(el("small", "", label), el("strong", "", value));
      metrics.append(cell);
    }
    result.append(metrics);

    result.append(el("h3", "review-subtitle", "Riesgos detectados"));
    const notes = el("ul", "review-notes");
    const items = Array.isArray(payload.observations) && payload.observations.length
      ? payload.observations : ["No hay observaciones suficientes para justificar una operación."];
    for (const note of items) notes.append(el("li", "", note));
    result.append(notes);

    result.append(el("p", "review-disclaimer",
      "Solo análisis. La orden se introdujo manualmente; no está sincronizada con Binance. No se verificó saldo ni ejecución y no se realizó ninguna operación."));
  }
  async function review(event) {
    if (event) event.preventDefault();
    const data = Object.fromEntries(new FormData(form).entries());
    result.textContent = "Analizando la orden y las cuatro temporalidades…";
    try {
      const response = await fetch("/orders/review", {
        method: "POST", headers: {"Content-Type": "application/json"},
        body: JSON.stringify(data), cache: "no-store"
      });
      const payload = await response.json();
      if (!response.ok) {
        result.textContent = "No se pudo evaluar: " +
          String(typeof payload.detail === "string" ? payload.detail : "HTTP " + response.status) +
          ". No operar.";
        return;
      }
      render(payload);
    } catch (_) {
      result.textContent = "Servicio no disponible. Orden sin verificar. NO OPERAR.";
    }
  }
  const button = document.getElementById("review-order-button");
  if (button) button.addEventListener("click", review);
  form.addEventListener("submit", review);
  result.textContent = "Introduce una orden de referencia y pulsa «Evaluar riesgo». No se ejecutarán operaciones.";
})();

"use strict";
// Manual reference only. Never persist credentials or submit orders.
(function () {
  const form = document.getElementById("order-review-form");
  const result = document.getElementById("order-review-result");
  if (!form || !result) return;

  async function review(event) {
    if (event) event.preventDefault();
    const data = Object.fromEntries(new FormData(form).entries());
    result.textContent = "Consultando mercado y evaluando orden manual...";
    try {
      const response = await fetch("/orders/review", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(data),
        cache: "no-store"
      });
      const payload = await response.json();
      if (!response.ok) {
        result.textContent = "No se pudo evaluar: " + String(
          typeof payload.detail === "string" ? payload.detail : "HTTP " + response.status
        );
        return;
      }
      const notes = Array.isArray(payload.observations) ? payload.observations.join(" ") : "";
      result.textContent =
        "ORDEN NO VERIFICADA · " + payload.symbol + " · " +
        payload.quantity + " unidades a " + payload.limit_price + " USDT. " +
        "Referencia 15m: " + payload.reference_close_15m + " USDT. " +
        "Distancia al límite: " + payload.distance_to_limit_pct + "%. " +
        "Importe nominal: " + payload.nominal_usdt + " USDT. " +
        "Contexto: " + payload.market_context + ". " + notes +
        " Solo revisión. No se realizó ninguna operación.";
    } catch (_) {
      result.textContent = "Sin respuesta del servicio. Orden sin verificar. NO OPERAR.";
    }
  }
  const button = document.getElementById("review-order-button");
  if (button) button.addEventListener("click", review);
  form.addEventListener("submit", review);
  result.textContent = "Evaluador listo. Pulsa «Revisar orden» para consultar datos públicos de Binance. La orden no está verificada.";
})();

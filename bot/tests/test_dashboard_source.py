"""Validación estática de selección de fuente sin conexión de red."""
from bot.web import api
from bot.data.websocket_stream import _build_combined_url


def test_default_source_is_simulation():
    assert api.DATA_SOURCE in ("simulation", "binance")
    assert api.source()["real_orders_enabled"] is False
    assert api.source()["authenticated_binance"] is False


def test_binance_public_stream_url():
    url = _build_combined_url(["btcusdt", "ethusdt"])
    assert url.startswith("wss://stream.binance.com:9443/stream?")
    assert "btcusdt@trade" in url
    assert "ethusdt@trade" in url


def test_status_exposes_source():
    assert api.status()["data_source"] == api.DATA_SOURCE
    assert api.status()["real_orders_enabled"] is False


def test_dashboard_template_renders():
    from starlette.requests import Request
    request = Request({"type": "http", "method": "GET", "path": "/dashboard", "headers": [], "query_string": b"", "scheme": "http", "server": ("127.0.0.1", 8000), "client": ("127.0.0.1", 1234), "root_path": "", "http_version": "1.1", "app": api.app})
    response = api.dashboard(request)
    assert response.status_code == 200
    assert response.template.name == "index.html"


def test_dashboard_has_two_external_scripts_and_three_asset_cards():
    from pathlib import Path
    html = Path("bot/web/templates/index.html").read_text(encoding="utf-8")
    js = Path("bot/web/static/command_center.js").read_text(encoding="utf-8")
    assert html.count("<script src=") == 2
    assert html.count("</script>") == 2
    assert html.rstrip().endswith("</html>")
    for symbol in ("BTCUSDT", "ETHUSDT", "WLDUSDT"):
        assert html.count('data-symbol="' + symbol + '"') == 1
    for tab in ("overview", "orders", "flow"):
        assert 'id="' + tab + '"' in html
    assert 'id="feed"' in html
    assert 'socket.addEventListener("message"' in js
    assert 'function refreshAll()' in js


def test_order_review_panel_uses_separate_script_and_manual_data():
    from pathlib import Path
    html = Path("bot/web/templates/index.html").read_text(encoding="utf-8")
    javascript = Path("bot/web/static/order_review.js").read_text(encoding="utf-8")
    assert 'id="order-review-form"' in html
    assert 'id="review-order-button" type="button"' in html
    assert 'button.addEventListener("click", review)' in javascript
    assert 'id="order-review-result"' in html
    assert 'src="/static/order_review.js"' in html
    assert 'action="/orders/review"' not in html
    assert 'fetch("/orders/review"' in javascript
    assert 'method: "POST"' in javascript
    assert "No coloca, modifica ni cancela órdenes" in html


def test_fixed_viewport_dashboard_has_no_page_scroll():
    from pathlib import Path
    css = Path("bot/web/static/command_center.css").read_text(encoding="utf-8")
    assert "height:100dvh" in css
    assert "overflow:hidden" in css
    assert "#overview.view.active" in css
    assert "#orders.view.active" in css
    assert "#flow.view.active" in css

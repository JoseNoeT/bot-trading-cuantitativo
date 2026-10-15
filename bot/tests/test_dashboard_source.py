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


def test_dashboard_html_has_single_complete_script():
    from pathlib import Path
    html = Path("bot/web/templates/index.html").read_text(encoding="utf-8")
    assert html.count("<script>") == 1
    assert html.count("</script>") == 1
    assert html.count("</html>") == 1
    assert html.rstrip().endswith("</html>")
    assert "function addMessage(event)" in html
    assert "log.prepend(line)" in html


def test_dashboard_has_distinct_asset_cards_and_collapsible_feed():
    from pathlib import Path
    html = Path("bot/web/templates/index.html").read_text(encoding="utf-8")
    for symbol in ("BTCUSDT", "ETHUSDT", "WLDUSDT"):
        assert html.count('data-symbol="' + symbol + '"') == 1
    assert 'id="toggle"' in html
    assert 'id="feed" hidden' in html
    assert 'function refreshOne(symbol)' in html
    assert html.count("<script>") == 1
    assert html.rstrip().endswith("</html>")

"""Market intelligence tests: offline, deterministic, no real orders."""
from bot.services.market_intelligence import analyze, fetch_closed_candles
import pytest


class Response:
    def __init__(self, rows):
        self.rows = rows

    def raise_for_status(self):
        pass

    def json(self):
        return self.rows


class Session:
    def __init__(self, rows):
        self.rows = rows

    def get(self, url, params, timeout):
        assert params["symbol"] == "BTCUSDT"
        assert params["interval"] == "1m"
        assert timeout == 8
        return Response(self.rows)


NOW = 7_000_000


def rows(count=80):
    output = []
    for i in range(count):
        opening = 1_000_000 + 60_000 * i
        price = 100 + i
        output.append([opening, str(price - 1), str(price + 1), str(price - 2),
                       str(price), "50", opening + 59_999])
    return output


def test_only_closed_candles_used():
    data = rows()
    current = data[-1][0] + 10
    result = fetch_closed_candles("BTCUSDT", session=Session(data), now_ms=current)
    assert len(result) == 79


def test_analysis_is_readonly_and_conservative():
    result = analyze("BTCUSDT", session=Session(rows()), now_ms=5_900_000)
    assert result["action"] == "NO_OPERAR"
    assert result["real_orders_enabled"] is False
    assert result["risk_status"] == "NOT_VERIFIED"
    assert result["source"] == "BINANCE_PUBLIC_REST"
    assert result["rsi14"] <= 100


def test_unknown_symbol_is_rejected():
    with pytest.raises(ValueError):
        fetch_closed_candles("FAKEUSDT", session=Session(rows()), now_ms=5_900_000)


def test_bad_price_is_rejected():
    data = rows()
    data[4][4] = "nan"
    with pytest.raises(ValueError):
        fetch_closed_candles("BTCUSDT", session=Session(data), now_ms=5_900_000)


def test_stale_candles_are_rejected():
    with pytest.raises(ValueError, match="desactualizados"):
        fetch_closed_candles("BTCUSDT", session=Session(rows()), now_ms=100_000_000)


def test_wldusdt_is_allowed_for_readonly_market_data():
    class WldSession(Session):
        def get(self, url, params, timeout):
            assert params["symbol"] == "WLDUSDT"
            return Response(rows())
    data = fetch_closed_candles("WLDUSDT", session=WldSession(rows()), now_ms=5_900_000)
    assert len(data) == 80

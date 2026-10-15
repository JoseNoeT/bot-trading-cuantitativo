"""Offline top-down tests. No network and no order execution."""
from bot.services.multitimeframe import TIMEFRAMES, analyze_multitimeframe
from bot.services.market_intelligence import fetch_closed_candles, INTERVAL_MS
import pytest


class Reply:
    def __init__(self, data):
        self.data = data

    def raise_for_status(self):
        return None

    def json(self):
        return self.data


class FakeSession:
    def __init__(self, falling=False):
        self.calls = []
        self.falling = falling

    def get(self, url, params, timeout):
        interval = params["interval"]
        self.calls.append(interval)
        step = INTERVAL_MS[interval]
        rows = []
        for i in range(100):
            opened = 1_000_000 + i * step
            price = (200 - i) if self.falling else (100 + i)
            rows.append([opened, str(price - 0.3), str(price + 0.5), str(price - 0.5),
                         str(price), "200", opened + step - 1])
        return Reply(rows)


def test_all_timeframes_use_closed_candles_and_no_orders():
    session = FakeSession()
    now = 1_000_000 + 100 * INTERVAL_MS["1d"] + 1_000
    result = analyze_multitimeframe("WLDUSDT", session=session, now_ms=now)
    assert session.calls == list(TIMEFRAMES)
    assert set(result["timeframes"]) == set(TIMEFRAMES)
    assert result["context"] == "ALCISTA_ALINEADO"
    assert result["action"] == "NO_OPERAR"
    assert result["real_orders_enabled"] is False


def test_falling_long_term_context_is_not_a_buy_signal():
    session = FakeSession(falling=True)
    now = 1_000_000 + 100 * INTERVAL_MS["1d"] + 1_000
    result = analyze_multitimeframe("WLDUSDT", session=session, now_ms=now)
    assert result["context"] == "BAJISTA_DOMINANTE"
    assert result["action"] == "NO_OPERAR"


def test_invalid_timeframe_is_blocked():
    with pytest.raises(ValueError, match="Temporalidad no permitida"):
        fetch_closed_candles("WLDUSDT", interval="3m", session=FakeSession())

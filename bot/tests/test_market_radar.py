"""Offline safety tests for the experimental radar."""
import pytest
from bot.services.market_radar import market_radar


def candles():
    return [{"timestamp": i * 60, "open": 1, "high": 1.1, "low": .9,
             "close": 1, "volume": 10} for i in range(100)]


def test_radar_is_read_only(monkeypatch):
    monkeypatch.setattr("bot.services.market_radar.fetch_closed_candles", lambda symbol, **kwargs: candles())
    out = market_radar("WLDUSDT")
    assert out["action"] == "OBSERVAR"
    assert out["real_orders_enabled"] is False
    assert out["whale_confirmed"] is False
    assert out["volume_relative"] == 1
    assert not any(out["flags"].values())


def test_radar_raises_on_invalid_market_data(monkeypatch):
    monkeypatch.setattr("bot.services.market_radar.fetch_closed_candles", lambda symbol, **kwargs: [])
    with pytest.raises(ValueError, match="insuficientes"):
        market_radar("WLDUSDT")

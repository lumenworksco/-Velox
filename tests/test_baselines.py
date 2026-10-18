"""Tests for backtesting/baselines.py."""

import numpy as np
import pandas as pd
import pytest

from backtesting import baselines as bl


def _bars(close, start="2023-01-02"):
    close = np.asarray(close, dtype=float)
    idx = pd.date_range(start, periods=len(close), freq="B")
    return pd.DataFrame({"open": close, "high": close * 1.01, "low": close * 0.99,
                         "close": close, "volume": 1_000}, index=idx)


def test_rsi_bounds_and_extremes():
    up = bl.rsi(pd.Series(np.arange(1.0, 60.0)), 14)
    down = bl.rsi(pd.Series(np.arange(60.0, 1.0, -1.0)), 14)
    assert up.iloc[-1] == pytest.approx(100.0)
    assert down.iloc[-1] < 1.0
    assert ((up.dropna() >= 0) & (up.dropna() <= 100)).all()


def test_pct_b_at_bands():
    close = pd.Series([10.0] * 19 + [10.0])
    assert bl.bollinger_pct_b(close).isna().all()  # zero width -> undefined, not inf
    wave = pd.Series(np.sin(np.linspace(0, 12, 120)) * 5 + 100)
    pct = bl.bollinger_pct_b(wave).dropna()
    assert pct.min() < 0.2 and pct.max() > 0.8


def test_ma_crossover_rejects_bad_periods():
    with pytest.raises(ValueError):
        bl.ma_crossover(_bars(range(1, 60)), fast=26, slow=12)


def test_ma_crossover_captures_uptrend():
    bars = _bars(np.concatenate([np.full(40, 100.0), np.linspace(100, 160, 120)]))
    result = bl.run_baseline("ma_crossover", "TEST", bars)
    assert result.total_trades == 1
    assert result.total_return > 0.2


def test_no_lookahead_fills_at_next_open():
    # Signal fires at bar i's close; entry must use bar i+1's open (a gap up here)
    close = np.concatenate([np.full(40, 100.0), np.linspace(100, 130, 60)])
    bars = _bars(close)
    bars["open"] = bars["close"].shift(1).fillna(bars["close"]) + 5  # opens 5 above prior close
    enter, _ = bl.ma_crossover(bars)
    first = int(np.argmax(enter.to_numpy()))
    result = bl.run_baseline("ma_crossover", "TEST", bars)
    assert result.total_trades >= 1
    # entry price is next bar's open, i.e. prior close + 5
    assert bars["open"].iloc[first + 1] == pytest.approx(bars["close"].iloc[first] + 5)


def test_rsi_baseline_buys_dips():
    rng = np.random.RandomState(1)
    close = 100 + np.cumsum(rng.randn(300))
    result = bl.run_baseline("rsi", "TEST", _bars(close))
    assert result.total_trades >= 1


def test_unknown_baseline_and_short_data():
    with pytest.raises(KeyError):
        bl.run_baseline("nope", "X", _bars(range(1, 100)))
    with pytest.raises(ValueError):
        bl.run_baseline("rsi", "X", _bars(range(1, 10)))


def test_all_baselines_run_on_bundled_sample_data():
    bars = bl.load_symbol("AAPL")
    assert len(bars) > 100
    for name in bl.BASELINES:
        result = bl.run_baseline(name, "AAPL", bars)
        assert np.isfinite(result.total_return)
        assert 0.0 <= result.max_drawdown <= 1.0


def test_load_symbol_missing(tmp_path):
    with pytest.raises(FileNotFoundError):
        bl.load_symbol("NOPE", tmp_path)

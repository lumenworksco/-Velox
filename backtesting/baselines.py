"""Classic baseline strategies for benchmarking Velox against.

Ported from the predecessor Rust project (its history lives under legacy/trading-algorithms): MA
crossover, RSI reversal, momentum and Bollinger-band mean reversion. They run
on daily bars, long-only, one symbol at a time, with signals computed at the
close and filled at the next bar's open (no look-ahead). They are not traded
live; ``velox backtest`` uses them as yardsticks for the production strategies.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Callable

import numpy as np
import pandas as pd

from backtester import BacktestResult, BacktestTrade, _compute_result

SAMPLE_DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "samples"


# ---------------------------------------------------------------------------
# Indicators
# ---------------------------------------------------------------------------

def ema(close: pd.Series, period: int) -> pd.Series:
    return close.ewm(span=period, adjust=False).mean()


def rsi(close: pd.Series, period: int = 14) -> pd.Series:
    """Wilder RSI (0-100)."""
    delta = close.diff()
    gain = delta.clip(lower=0).ewm(alpha=1 / period, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1 / period, adjust=False).mean()
    rs = gain / loss.replace(0, np.nan)
    out = 100 - 100 / (1 + rs)
    return out.where(loss != 0, 100.0)


def bollinger_pct_b(close: pd.Series, period: int = 20, num_std: float = 2.0) -> pd.Series:
    """%B: 0 at the lower band, 1 at the upper band."""
    mid = close.rolling(period).mean()
    std = close.rolling(period).std(ddof=0)
    width = (2 * num_std * std).replace(0, np.nan)
    return (close - (mid - num_std * std)) / width


# ---------------------------------------------------------------------------
# Signal generators: bars -> (enter, exit) boolean Series, evaluated at the close
# ---------------------------------------------------------------------------

def ma_crossover(bars: pd.DataFrame, fast: int = 12, slow: int = 26,
                 threshold: float = 0.001):
    if fast >= slow:
        raise ValueError("fast period must be smaller than slow period")
    spread = (ema(bars["close"], fast) - ema(bars["close"], slow)) / ema(bars["close"], slow)
    return spread > threshold, spread < -threshold


def rsi_reversal(bars: pd.DataFrame, period: int = 14, oversold: float = 30.0,
                 exit_overbought: float = 70.0):
    r = rsi(bars["close"], period)
    return r < oversold, r > exit_overbought


def momentum(bars: pd.DataFrame, period: int = 10, fast: int = 12, slow: int = 26,
             rsi_period: int = 14, rsi_long: float = 50.0, min_momentum: float = 0.02):
    close = bars["close"]
    mom = close / close.shift(period) - 1
    trend_up = ema(close, fast) > ema(close, slow)
    enter = (mom > min_momentum) & trend_up & (rsi(close, rsi_period) > rsi_long)
    return enter, (mom <= 0) | ~trend_up


def bollinger_reversion(bars: pd.DataFrame, period: int = 20, num_std: float = 2.0,
                        entry: float = 0.05, exit_: float = 0.5):
    pct_b = bollinger_pct_b(bars["close"], period, num_std)
    return pct_b <= entry, pct_b >= exit_


@dataclass(frozen=True)
class Baseline:
    name: str
    description: str
    signals: Callable[..., tuple[pd.Series, pd.Series]]
    warmup: int = field(default=30)


BASELINES: dict[str, Baseline] = {b.name: b for b in [
    Baseline("ma_crossover", "EMA(12/26) crossover trend follower", ma_crossover, 30),
    Baseline("rsi", "RSI(14) oversold entry, overbought exit", rsi_reversal, 20),
    Baseline("momentum", "10-bar momentum confirmed by EMA trend and RSI", momentum, 30),
    Baseline("mean_reversion", "Bollinger(20, 2) %B mean reversion", bollinger_reversion, 25),
]}


# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------

def load_csv(path: str | Path) -> pd.DataFrame:
    """Load OHLCV bars from CSV (columns: timestamp, open, high, low, close, volume)."""
    df = pd.read_csv(path, parse_dates=["timestamp"], index_col="timestamp").sort_index()
    df.columns = [c.lower() for c in df.columns]
    missing = {"open", "close"} - set(df.columns)
    if missing:
        raise ValueError(f"{path}: missing columns {sorted(missing)}")
    return df


def load_symbol(symbol: str, csv_dir: str | Path = SAMPLE_DATA_DIR) -> pd.DataFrame:
    path = Path(csv_dir) / f"{symbol.lower()}_daily.csv"
    if not path.exists():
        raise FileNotFoundError(f"No CSV for {symbol} at {path}")
    return load_csv(path)


def fetch_daily(symbol: str, start: str, end: str) -> pd.DataFrame:
    """Daily bars from yfinance."""
    import yfinance as yf

    df = yf.Ticker(symbol).history(start=start, end=end, interval="1d", auto_adjust=True)
    if df.empty:
        raise ValueError(f"No data returned for {symbol}")
    df.columns = [c.lower() for c in df.columns]
    df.index = df.index.tz_localize(None)
    return df


# ---------------------------------------------------------------------------
# Simulation
# ---------------------------------------------------------------------------

def run_baseline(name: str, symbol: str, bars: pd.DataFrame,
                 initial_capital: float = 100_000.0,
                 commission_pct: float = 0.0005, **params) -> BacktestResult:
    """Backtest one baseline on one symbol. Long-only, fully invested while in a trade."""
    if name not in BASELINES:
        raise KeyError(f"Unknown baseline '{name}'. Available: {', '.join(BASELINES)}")
    baseline = BASELINES[name]
    if len(bars) <= baseline.warmup + 1:
        raise ValueError(f"{symbol}: need more than {baseline.warmup + 1} bars, got {len(bars)}")

    enter, exit_ = baseline.signals(bars, **params)
    opens, closes = bars["open"].to_numpy(), bars["close"].to_numpy()
    index = bars.index
    enter_v, exit_v = enter.fillna(False).to_numpy(), exit_.fillna(False).to_numpy()

    cash, qty, entry_px, entry_i = initial_capital, 0, 0.0, 0
    trades: list[BacktestTrade] = []
    history = [initial_capital]

    def close_position(i: int, px: float):
        nonlocal cash, qty
        fee = px * qty * commission_pct
        cash += px * qty - fee
        trades.append(BacktestTrade(
            symbol=symbol, strategy=name, side="buy", entry_price=entry_px,
            entry_time=index[entry_i].to_pydatetime(), qty=qty, exit_price=px,
            exit_time=index[i].to_pydatetime(),
            pnl=(px - entry_px) * qty - fee - entry_fee,
            commission=fee + entry_fee,
        ))
        qty = 0

    entry_fee = 0.0
    for i in range(baseline.warmup, len(bars) - 1):
        # Signals from bar i's close fill at bar i+1's open
        fill = opens[i + 1]
        if qty == 0 and enter_v[i] and not exit_v[i]:
            shares = int(cash / (fill * (1 + commission_pct)))
            if shares > 0:
                entry_fee = fill * shares * commission_pct
                cash -= fill * shares + entry_fee
                qty, entry_px, entry_i = shares, fill, i + 1
        elif qty > 0 and exit_v[i]:
            close_position(i + 1, fill)
        history.append(cash + qty * closes[i + 1])

    if qty > 0:  # mark the final open position to the last close
        close_position(len(bars) - 1, closes[-1])
        history[-1] = cash

    result = _compute_result(f"{name}:{symbol}", trades, history, initial_capital)
    if not trades:
        return result
    # _compute_result annualises over days that had a trade; these are daily
    # equity curves, so annualise over the whole window instead.
    equity = np.asarray(history)
    daily = np.diff(equity) / equity[:-1]
    sharpe = float(daily.mean() / daily.std(ddof=1) * np.sqrt(252)) if daily.std(ddof=1) > 0 else 0.0
    annualized = float((equity[-1] / equity[0]) ** (252 / len(daily)) - 1)
    return replace(result, sharpe_ratio=sharpe, annualized_return=annualized)


def buy_and_hold(bars: pd.DataFrame) -> float:
    """Total return of holding the symbol over the same window (the benchmark)."""
    return float(bars["close"].iloc[-1] / bars["open"].iloc[0] - 1)

"""Render the Rich terminal dashboard with synthetic data (no broker needed).

Useful for screenshots and for previewing dashboard changes:

    TESTING=1 python scripts/demo_dashboard.py

All numbers below are made up.
"""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

os.environ.setdefault("TESTING", "1")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import config  # noqa: E402
from dashboard import build_dashboard, console  # noqa: E402
from risk import RiskManager  # noqa: E402
from risk.risk_manager import TradeRecord  # noqa: E402


def _trade(symbol, strategy, side, entry, qty, minutes_ago, **kw):
    now = datetime.now(config.ET)
    return TradeRecord(
        symbol=symbol, strategy=strategy, side=side, entry_price=entry,
        entry_time=now - timedelta(minutes=minutes_ago), qty=qty,
        take_profit=entry * 1.01, stop_loss=entry * 0.99, **kw,
    )


def main():
    now = datetime.now(config.ET)
    risk = RiskManager()
    risk.reset_daily(104_820.0, 61_340.0)
    risk.current_equity = 106_240.0
    risk.day_pnl = 0.0136

    for t in [
        _trade("AAPL", "STAT_MR", "buy", 231.40, 60, 42),
        _trade("MSFT", "STAT_MR", "sell", 428.10, 30, 18),
        _trade("XOM", "KALMAN_PAIRS", "buy", 112.85, 120, 1500, hold_type="swing", pair_id="xomcvx01"),
        _trade("CVX", "KALMAN_PAIRS", "sell", 158.20, 85, 1500, hold_type="swing", pair_id="xomcvx01"),
        _trade("NVDA", "PEAD", "buy", 141.55, 45, 2900, hold_type="swing"),
    ]:
        risk.open_trades[t.symbol] = t

    for sym, strat, side, entry, qty, pnl, reason, mins in [
        ("JPM", "STAT_MR", "buy", 241.10, 50, 38.5, "take_profit", 95),
        ("AMD", "VWAP", "buy", 158.90, 70, -22.4, "stop_loss", 70),
        ("GOOG", "STAT_MR", "sell", 176.30, 60, 51.2, "mr_reverted", 48),
        ("META", "MICRO_MOM", "buy", 574.00, 15, 18.9, "time_stop", 30),
        ("BAC", "VWAP", "buy", 44.60, 200, 27.0, "take_profit", 22),
        ("INTC", "STAT_MR", "buy", 23.15, 300, 41.7, "take_profit", 9),
    ]:
        t = _trade(sym, strat, side, entry, qty, mins + 25)
        t.pnl, t.exit_reason, t.status = pnl, reason, "closed"
        t.exit_price, t.exit_time = entry, now - timedelta(minutes=mins)
        risk.closed_trades.append(t)

    analytics = {
        "sharpe_7d": 1.84, "win_rate": 0.68, "profit_factor": 1.92,
        "max_drawdown": 0.021, "week_pnl": 2_480.0, "week_pnl_pct": 0.0239,
        "strategy_breakdown": {
            "STAT_MR": {"trades": 21, "win_rate": 0.71, "pnl": 1_120.0},
            "VWAP": {"trades": 12, "win_rate": 0.58, "pnl": 240.0},
            "KALMAN_PAIRS": {"trades": 4, "win_rate": 0.75, "pnl": 610.0},
            "PEAD": {"trades": 3, "win_rate": 0.67, "pnl": 380.0},
            "MICRO_MOM": {"trades": 5, "win_rate": 0.60, "pnl": 130.0},
        },
    }

    panel = build_dashboard(
        risk, "BULLISH", now - timedelta(hours=3, minutes=12), now,
        now - timedelta(seconds=40), 127, analytics,
        vol_scalar=1.08, portfolio_beta=0.12, consistency_score=78,
        hmm_regime_state="BULL", hmm_probabilities={"BULL": 0.72, "NEUTRAL": 0.2, "BEAR": 0.08},
        cross_asset_bias=0.15, portfolio_heat_pct=34.0, overnight_count=3,
    )
    console.print(panel)


if __name__ == "__main__":
    main()

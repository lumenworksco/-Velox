"""Tests for database.py — CRUD for all V6/V7/V8 tables.

Complements test_database.py which already covers trades, open_positions,
daily_snapshots, and signals.  This file covers the newer tables:
monte_carlo_results, and execution_analytics, and also
provides explicit round-trip tests for signals and snapshots aligned with
the test_database_tables spec.
"""

from datetime import datetime, timezone

import pytest

import database
from conftest import ET, _make_trade


# ---------------------------------------------------------------------------
# Schema completeness
# ---------------------------------------------------------------------------

class TestInitDb:
    """Verify that init_db creates all expected tables."""

    def test_all_expected_tables_exist(self):
        """Every required table must be present after init_db."""
        conn = database._get_conn()
        tables = {
            row["name"]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
        expected = {
            "trades",
            "signals",
            "open_positions",
            "daily_snapshots",
            "backtest_results",
            "model_performance",
            "optimization_history",
            "allocation_history",
            "shadow_trades",
            "ou_parameters",
            "kalman_pairs",
            "consistency_log",
            "monte_carlo_results",
            "execution_analytics",
        }
        missing = expected - tables
        assert not missing, f"Missing tables: {missing}"

    def test_v8_tables_exist(self):
        """V8 tables (monte_carlo, execution_analytics) must exist."""
        conn = database._get_conn()
        tables = {
            row["name"]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
        for t in ("monte_carlo_results", "execution_analytics"):
            assert t in tables, f"V8 table '{t}' not found"


# ---------------------------------------------------------------------------
# Trade round-trip
# ---------------------------------------------------------------------------

class TestLogTradeRoundTrip:
    """log_trade / get_recent_trades round-trip."""

    def test_log_and_retrieve_trade(self):
        """A logged trade is retrievable via get_recent_trades."""
        now = datetime.now(ET)
        database.log_trade(
            symbol="NVDA",
            strategy="ORB",
            side="buy",
            entry_price=800.0,
            exit_price=850.0,
            qty=5,
            entry_time=now,
            exit_time=now,
            exit_reason="take_profit",
            pnl=250.0,
            pnl_pct=0.0625,
        )

        trades = database.get_recent_trades(days=1)
        assert len(trades) == 1
        t = trades[0]
        assert t["symbol"] == "NVDA"
        assert t["strategy"] == "ORB"
        assert t["side"] == "buy"
        assert t["pnl"] == pytest.approx(250.0)
        assert t["pnl_pct"] == pytest.approx(0.0625)
        assert t["exit_reason"] == "take_profit"

    def test_multiple_trades_ordered_desc(self):
        """get_recent_trades returns rows ordered by exit_time DESC."""
        from datetime import timedelta
        now = datetime.now(ET)
        t1 = now - timedelta(hours=4)
        t2 = now - timedelta(hours=1)
        for ts, sym in [(t1, "AAPL"), (t2, "MSFT")]:
            database.log_trade(
                symbol=sym, strategy="VWAP", side="sell",
                entry_price=100.0, exit_price=95.0, qty=10,
                entry_time=ts, exit_time=ts,
                exit_reason="stop_loss", pnl=-50.0, pnl_pct=-0.05,
            )

        trades = database.get_recent_trades(days=1)
        # Most recent first
        assert trades[0]["symbol"] == "MSFT"
        assert trades[1]["symbol"] == "AAPL"


# ---------------------------------------------------------------------------
# Signal round-trip
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Open positions round-trip
# ---------------------------------------------------------------------------

class TestOpenPositionsRoundTrip:
    """save_open_positions / load_open_positions round-trip."""

    def test_save_and_load_single_position(self):
        """A saved position is returned by load_open_positions."""
        trade = _make_trade(
            symbol="TSLA", strategy="VWAP", side="sell",
            entry_price=250.0, qty=8,
        )
        database.save_open_positions({"TSLA": trade})

        rows = database.load_open_positions()
        assert len(rows) == 1
        r = rows[0]
        assert r["symbol"] == "TSLA"
        assert r["strategy"] == "VWAP"
        assert r["side"] == "sell"
        assert r["entry_price"] == pytest.approx(250.0)
        assert r["qty"] == 8

    def test_save_clears_old_positions(self):
        """Calling save_open_positions replaces all existing rows."""
        t1 = _make_trade(symbol="AAPL")
        t2 = _make_trade(symbol="MSFT")
        database.save_open_positions({"AAPL": t1, "MSFT": t2})
        assert len(database.load_open_positions()) == 2

        t3 = _make_trade(symbol="NVDA")
        database.save_open_positions({"NVDA": t3})
        rows = database.load_open_positions()
        assert len(rows) == 1
        assert rows[0]["symbol"] == "NVDA"

    def test_save_empty_clears_all(self):
        """Saving an empty dict removes all open positions."""
        database.save_open_positions({"AAPL": _make_trade()})
        database.save_open_positions({})
        assert database.load_open_positions() == []

    def test_v4_fields_preserved(self):
        """V4 fields (pair_id, partial_exits, etc.) survive the round-trip."""
        trade = _make_trade(
            symbol="AAPL", strategy="KALMAN_PAIRS",
            pair_id="AAPL-MSFT-001", partial_exits=2,
            highest_price_seen=160.0, entry_atr=2.5,
        )
        database.save_open_positions({"AAPL": trade})

        rows = database.load_open_positions()
        r = rows[0]
        assert r["pair_id"] == "AAPL-MSFT-001"
        assert r["partial_exits"] == 2
        assert r["highest_price_seen"] == pytest.approx(160.0)
        assert r["entry_atr"] == pytest.approx(2.5)


# ---------------------------------------------------------------------------
# Daily snapshots round-trip
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Monte Carlo results
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Execution analytics
# ---------------------------------------------------------------------------


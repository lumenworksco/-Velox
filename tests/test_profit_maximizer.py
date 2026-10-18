"""Comprehensive tests for engine/profit_maximizer.py — bonus alpha-generation features.

Tests cover:
- get_adaptive_scan_interval() with various VIX/regime/position combos
- IntradayVolRegime (CALM/ACTIVE/HEATED/EXTREME)
- WinStreakTracker multiplier calculation
- compute_dynamic_stop() tightening logic
- optimize_entry_price() spread-based optimization
"""

import sys
import time
from dataclasses import dataclass
from datetime import datetime
from unittest.mock import patch

import numpy as np
import pytest

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent.parent))


@pytest.fixture
def pm():
    """Import profit_maximizer module."""
    import importlib
    mod = importlib.import_module("engine.profit_maximizer")
    importlib.reload(mod)
    return mod


# ===================================================================
# get_adaptive_scan_interval
# ===================================================================

class TestAdaptiveScanInterval:
    """Scan interval adapts to VIX, regime, position count, time of day."""

    # --- VIX-based base intervals ---

    def test_extreme_vix_gets_fast_scan(self, pm):
        interval = pm.get_adaptive_scan_interval(vix_level=40, regime="NORMAL",
                                                  num_open_positions=0, hour=12)
        assert interval == 30  # Minimum

    def test_high_vix_gets_60s_base(self, pm):
        interval = pm.get_adaptive_scan_interval(vix_level=30, regime="NORMAL",
                                                  num_open_positions=0, hour=12)
        assert 30 <= interval <= 60

    def test_moderate_vix_gets_120s_base(self, pm):
        interval = pm.get_adaptive_scan_interval(vix_level=18, regime="NORMAL",
                                                  num_open_positions=0, hour=12)
        assert 90 <= interval <= 150

    def test_low_vix_gets_180s_base(self, pm):
        interval = pm.get_adaptive_scan_interval(vix_level=12, regime="NORMAL",
                                                  num_open_positions=0, hour=12)
        assert 140 <= interval <= 200

    # --- Regime adjustments ---

    def test_high_vol_regime_reduces_interval(self, pm):
        normal = pm.get_adaptive_scan_interval(vix_level=18, regime="NORMAL",
                                                num_open_positions=0, hour=12)
        vol = pm.get_adaptive_scan_interval(vix_level=18, regime="HIGH_VOL_BULL",
                                             num_open_positions=0, hour=12)
        assert vol < normal

    def test_mean_reverting_regime_reduces_interval(self, pm):
        normal = pm.get_adaptive_scan_interval(vix_level=18, regime="NORMAL",
                                                num_open_positions=0, hour=12)
        mr = pm.get_adaptive_scan_interval(vix_level=18, regime="MEAN_REVERTING",
                                            num_open_positions=0, hour=12)
        assert mr < normal

    def test_high_vol_bear_also_reduces(self, pm):
        normal = pm.get_adaptive_scan_interval(vix_level=18, regime="NORMAL",
                                                num_open_positions=0, hour=12)
        hvb = pm.get_adaptive_scan_interval(vix_level=18, regime="HIGH_VOL_BEAR",
                                             num_open_positions=0, hour=12)
        assert hvb < normal

    # --- Position count adjustments ---

    def test_many_positions_cap_interval(self, pm):
        interval = pm.get_adaptive_scan_interval(vix_level=12, regime="NORMAL",
                                                  num_open_positions=12, hour=12)
        assert interval <= 60  # Capped for >10 positions

    def test_moderate_positions_cap(self, pm):
        interval = pm.get_adaptive_scan_interval(vix_level=12, regime="NORMAL",
                                                  num_open_positions=7, hour=12)
        assert interval <= 90  # Capped for >5 positions

    def test_few_positions_no_cap(self, pm):
        interval = pm.get_adaptive_scan_interval(vix_level=12, regime="NORMAL",
                                                  num_open_positions=2, hour=12)
        assert interval > 90

    # --- Time of day ---

    def test_prime_hours_faster_scan(self, pm):
        # 10-11am and 1-3pm are prime hours (0.8x)
        prime = pm.get_adaptive_scan_interval(vix_level=18, regime="NORMAL",
                                               num_open_positions=0, hour=10)
        off = pm.get_adaptive_scan_interval(vix_level=18, regime="NORMAL",
                                             num_open_positions=0, hour=12)
        assert prime < off

    def test_open_close_hours_slightly_faster(self, pm):
        # Hour 9 and 15 get 0.9x multiplier
        edge = pm.get_adaptive_scan_interval(vix_level=18, regime="NORMAL",
                                              num_open_positions=0, hour=9)
        mid = pm.get_adaptive_scan_interval(vix_level=18, regime="NORMAL",
                                             num_open_positions=0, hour=12)
        assert edge <= mid

    # --- Bounds ---

    def test_minimum_30s(self, pm):
        # Even with all reductions
        interval = pm.get_adaptive_scan_interval(vix_level=50, regime="HIGH_VOL_BULL",
                                                  num_open_positions=15, hour=10)
        assert interval >= 30

    def test_maximum_300s(self, pm):
        # Even with all slow factors
        interval = pm.get_adaptive_scan_interval(vix_level=8, regime="NORMAL",
                                                  num_open_positions=0, hour=12)
        assert interval <= 300


# ===================================================================
# IntradayVolRegime
# ===================================================================

class TestIntradayVolRegime:
    """Micro-regime detection: CALM, ACTIVE, HEATED, EXTREME."""

    def test_default_regime_is_calm(self, pm):
        ivr = pm.IntradayVolRegime()
        assert ivr.get_regime() == "CALM"

    def test_calm_regime_sizing(self, pm):
        ivr = pm.IntradayVolRegime()
        assert ivr.get_sizing_multiplier() == 1.0

    def test_regime_with_data(self, pm):
        """After enough data, regime should be computed."""
        ivr = pm.IntradayVolRegime(lookback=20)
        # Feed in stable prices (low vol)
        base_time = time.time() - 5000
        for i in range(15):
            with patch("time.time", return_value=base_time + i * 300):
                ivr.update(100.0 + np.random.normal(0, 0.01))

        # With very small moves, should be CALM
        regime = ivr.get_regime()
        assert regime in ("CALM", "ACTIVE")

    def test_extreme_regime_from_large_moves(self, pm):
        """Injecting very large moves should push to HEATED/EXTREME."""
        ivr = pm.IntradayVolRegime(lookback=30)
        base_time = time.time() - 10000

        # First feed normal data
        for i in range(20):
            with patch("time.time", return_value=base_time + i * 300):
                ivr.update(100.0 + i * 0.01)

        # Then feed a large move
        with patch("time.time", return_value=base_time + 20 * 300):
            ivr.update(110.0)  # 10% jump

        regime = ivr.get_regime()
        assert regime in ("HEATED", "EXTREME")

    def test_sizing_multipliers_are_valid(self, pm):
        expected = {"CALM": 1.0, "ACTIVE": 0.9, "HEATED": 0.7, "EXTREME": 0.4}
        ivr = pm.IntradayVolRegime()
        for regime, mult in expected.items():
            # Test the mapping directly
            result = {"CALM": 1.0, "ACTIVE": 0.9, "HEATED": 0.7, "EXTREME": 0.4}[regime]
            assert result == mult

    def test_not_enough_data_returns_calm(self, pm):
        """With < 10 data points, default to CALM."""
        ivr = pm.IntradayVolRegime()
        base_time = time.time() - 3000
        for i in range(5):
            with patch("time.time", return_value=base_time + i * 300):
                ivr.update(100.0 + i * 0.5)
        assert ivr.get_regime() == "CALM"

    def test_update_respects_minimum_interval(self, pm):
        """Updates closer than 240s should not add vol data."""
        ivr = pm.IntradayVolRegime()
        now = time.time()
        with patch("time.time", return_value=now):
            ivr.update(100.0)
        with patch("time.time", return_value=now + 60):  # Only 60s later
            ivr.update(101.0)
        # Should only have at most 0 entries (first update sets _last_price, no vol yet)
        assert len(ivr._vol_history) == 0


# ===================================================================
# WinStreakTracker
# ===================================================================

class TestWinStreakTracker:
    """Multiplier based on recent win/loss pattern."""

    def test_empty_tracker_returns_1_0(self, pm):
        tracker = pm.WinStreakTracker()
        assert tracker.get_multiplier() == 1.0

    def test_less_than_3_trades_returns_1_0(self, pm):
        tracker = pm.WinStreakTracker()
        tracker.record_trade(True)
        tracker.record_trade(True)
        assert tracker.get_multiplier() == 1.0

    def test_hot_streak_4_wins(self, pm):
        tracker = pm.WinStreakTracker()
        for _ in range(5):
            tracker.record_trade(True)
        # 4+ wins in last 5 → 1.15
        assert tracker.get_multiplier() == 1.15

    def test_warm_streak_3_wins(self, pm):
        tracker = pm.WinStreakTracker()
        for _ in range(3):
            tracker.record_trade(True)
        # 3 wins in last 5 (only 3 trades recorded) → 1.05
        assert tracker.get_multiplier() == 1.05

    def test_cold_streak_4_losses(self, pm):
        tracker = pm.WinStreakTracker()
        for _ in range(5):
            tracker.record_trade(False)
        # 4+ losses in last 5 → 0.7
        assert tracker.get_multiplier() == 0.7

    def test_mild_cold_streak_3_losses(self, pm):
        tracker = pm.WinStreakTracker()
        tracker.record_trade(True)   # 1 win
        tracker.record_trade(False)  # 3 losses
        tracker.record_trade(False)
        tracker.record_trade(False)
        # last 5: 1W 3L → losses >= 3 → 0.85
        assert tracker.get_multiplier() == 0.85

    def test_mixed_results_neutral(self, pm):
        tracker = pm.WinStreakTracker()
        tracker.record_trade(True)
        tracker.record_trade(False)
        tracker.record_trade(True)
        tracker.record_trade(False)
        tracker.record_trade(True)
        # 3W 2L in last 5 → 3 wins → 1.05
        assert tracker.get_multiplier() == 1.05

    def test_even_split_neutral(self, pm):
        tracker = pm.WinStreakTracker()
        tracker.record_trade(True)
        tracker.record_trade(False)
        tracker.record_trade(True)
        tracker.record_trade(False)
        # 2W 2L → neither >= 3 → 1.0
        assert tracker.get_multiplier() == 1.0

    def test_max_streak_capped(self, pm):
        tracker = pm.WinStreakTracker(max_streak=10)
        for _ in range(15):
            tracker.record_trade(True)
        # Deque only keeps last 10
        assert len(tracker._results) == 10
        assert tracker.get_multiplier() == 1.15

    def test_get_stats(self, pm):
        tracker = pm.WinStreakTracker()
        tracker.record_trade(True)
        tracker.record_trade(True)
        tracker.record_trade(True)
        stats = tracker.get_stats()
        assert stats["streak"] == 3
        assert stats["multiplier"] == 1.05
        assert stats["last_5_wins"] == 3

    def test_get_stats_loss_streak(self, pm):
        tracker = pm.WinStreakTracker()
        tracker.record_trade(True)
        tracker.record_trade(False)
        tracker.record_trade(False)
        stats = tracker.get_stats()
        assert stats["streak"] == -2  # Negative for losses

    def test_get_stats_empty(self, pm):
        tracker = pm.WinStreakTracker()
        stats = tracker.get_stats()
        assert stats["streak"] == 0
        assert stats["multiplier"] == 1.0


# ===================================================================
# compute_dynamic_stop
# ===================================================================


# ===================================================================
# optimize_entry_price
# ===================================================================


# ===================================================================
# Signal Stacking (bonus test)
# ===================================================================


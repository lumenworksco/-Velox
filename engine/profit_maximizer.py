"""V12 BONUS: Profit Maximization Engine.

Additional alpha-generating and risk-adjusted return enhancements that go
beyond the core 85 V12 items. These features leverage existing infrastructure
(lead-lag analysis, alternative data, regime detection) to squeeze out
additional edge.

Features:
1. Adaptive Scan Frequency — faster scans in high-opportunity regimes
2. Signal Stacking — combine multiple weak signals into strong convictions
3. Momentum Persistence — hold winners longer when momentum confirms
4. Intraday Volatility Regime — micro-regime detection for tighter sizing
5. Cross-Asset Lead-Lag Trading — use SPY/VIX/TLT leads for entry timing
6. Post-Open Gap Fade Strategy — mean-revert 1-3% gaps
7. Dynamic Stop Tightening — tighten stops as position ages with profit
8. Conviction Pyramiding — add to winners at key levels
"""

import logging
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, time as dt_time, timedelta
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)


# ============================================================
# 1. Adaptive Scan Frequency
# ============================================================

def get_adaptive_scan_interval(
    vix_level: float,
    regime: str,
    num_open_positions: int,
    hour: int,
) -> int:
    """Return optimal scan interval in seconds based on market conditions.

    Goes beyond the basic VIX-based scaling in the main loop by also
    considering regime, position count, and time of day.

    Returns interval in seconds (30-300).
    """
    # Base from VIX
    if vix_level > 35:
        base = 30
    elif vix_level > 25:
        base = 60
    elif vix_level > 15:
        base = 120
    else:
        base = 180

    # Regime adjustment
    if regime in ("HIGH_VOL_BULL", "HIGH_VOL_BEAR"):
        base = int(base * 0.7)  # Scan more in volatile regimes
    elif regime == "MEAN_REVERTING":
        base = int(base * 0.85)  # MR signals are time-sensitive

    # Position count — more positions = need more monitoring
    if num_open_positions > 10:
        base = min(base, 60)
    elif num_open_positions > 5:
        base = min(base, 90)

    # Time of day — prime hours get faster scans
    if 10 <= hour < 11 or 13 <= hour < 15:
        base = int(base * 0.8)
    elif hour == 9 or hour == 15:
        base = int(base * 0.9)

    return max(30, min(300, base))


# ============================================================
# 2. Signal Stacking (Weak Signal Aggregation)
# ============================================================

@dataclass
class StackedSignal:
    """A signal constructed by combining multiple weak signals."""
    symbol: str
    direction: str       # "buy" or "sell"
    sources: list        # List of strategy names that agree
    avg_confidence: float
    combined_score: float


# ============================================================
# 3. Momentum Persistence — Hold Winners Longer
# ============================================================


# ============================================================
# 4. Dynamic Stop Tightening
# ============================================================


# ============================================================
# 5. Conviction Pyramiding
# ============================================================


# ============================================================
# 6. Intraday Volatility Micro-Regime
# ============================================================

class IntradayVolRegime:
    """Detect intraday volatility regime shifts for tighter position sizing.

    Tracks 5-minute realized vol and classifies into micro-regimes:
    - CALM: vol < 50th percentile of rolling window → normal sizing
    - ACTIVE: vol 50th-80th percentile → slightly reduced sizing (0.9x)
    - HEATED: vol 80th-95th percentile → reduced sizing (0.7x)
    - EXTREME: vol > 95th percentile → minimal sizing (0.4x)
    """

    def __init__(self, lookback: int = 78):  # 78 x 5-min = 6.5 hour day
        self._vol_history: deque[float] = deque(maxlen=lookback)
        self._last_price: Optional[float] = None
        self._last_update: float = 0

    def update(self, price: float) -> None:
        """Update with latest price. Call every ~5 minutes."""
        now = time.time()
        if self._last_price is not None and (now - self._last_update) >= 240:  # 4min min
            ret = abs(np.log(price / self._last_price))
            self._vol_history.append(ret)
        self._last_price = price
        self._last_update = now

    def get_regime(self) -> str:
        """Return current intraday volatility regime."""
        if len(self._vol_history) < 10:
            return "CALM"

        arr = np.array(self._vol_history)
        current = arr[-1] if len(arr) > 0 else 0
        p50 = np.percentile(arr, 50)
        p80 = np.percentile(arr, 80)
        p95 = np.percentile(arr, 95)

        if current > p95:
            return "EXTREME"
        elif current > p80:
            return "HEATED"
        elif current > p50:
            return "ACTIVE"
        return "CALM"

    def get_sizing_multiplier(self) -> float:
        """Return position sizing multiplier based on intraday vol regime."""
        regime = self.get_regime()
        return {
            "CALM": 1.0,
            "ACTIVE": 0.9,
            "HEATED": 0.7,
            "EXTREME": 0.4,
        }[regime]


# ============================================================
# 7. Spread-Adjusted Entry Optimization
# ============================================================


# ============================================================
# 8. Win Streak Bonus Sizing
# ============================================================

class WinStreakTracker:
    """Track consecutive wins/losses to adjust sizing.

    Psychological and statistical research shows momentum in trader
    performance. During win streaks, increase size modestly. During
    loss streaks, reduce size to limit damage.

    Multiplier range: 0.6x (losing streak) to 1.2x (winning streak).
    """

    def __init__(self, max_streak: int = 10):
        self._results: deque[bool] = deque(maxlen=max_streak)

    def record_trade(self, won: bool) -> None:
        self._results.append(won)

    def get_multiplier(self) -> float:
        if len(self._results) < 3:
            return 1.0

        recent = list(self._results)[-5:]  # Last 5 trades
        wins = sum(1 for r in recent if r)
        losses = len(recent) - wins

        if wins >= 4:
            return 1.15  # Slight boost on hot streak
        elif wins >= 3:
            return 1.05
        elif losses >= 4:
            return 0.7   # Reduce on cold streak
        elif losses >= 3:
            return 0.85
        return 1.0

    def get_stats(self) -> dict:
        if not self._results:
            return {"streak": 0, "multiplier": 1.0}
        recent = list(self._results)
        # Current streak
        streak = 0
        last = recent[-1]
        for r in reversed(recent):
            if r == last:
                streak += 1
            else:
                break
        return {
            "streak": streak if last else -streak,
            "multiplier": self.get_multiplier(),
            "last_5_wins": sum(1 for r in recent[-5:] if r),
        }

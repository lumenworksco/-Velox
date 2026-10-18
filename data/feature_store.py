"""DATA-002: Feature Store — online/offline feature computation and caching.

Provides a unified feature computation layer for all strategies.
Computes technical indicators (RSI, ATR, Bollinger, OBV, MFI, etc.),
volatility measures, return horizons, and price-relative-to-MA features.

Thread-safe with proper locking for concurrent strategy access.
"""

import logging
import threading
import time as _time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Feature metadata registry
# ---------------------------------------------------------------------------

@dataclass
class FeatureMeta:
    """Metadata for a registered feature."""
    name: str
    version: int = 1
    description: str = ""
    staleness_threshold_sec: float = 300.0  # 5 minutes default
    dependencies: list[str] = field(default_factory=list)
    compute_fn: Optional[Callable] = None  # set during registration


# ---------------------------------------------------------------------------
# Pure computation helpers (stateless, operate on numpy/pandas)
# ---------------------------------------------------------------------------

def _rsi(close: pd.Series, period: int) -> float:
    """Compute RSI for the most recent bar."""
    if len(close) < period + 1:
        return np.nan
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.iloc[-period:].mean()
    avg_loss = loss.iloc[-period:].mean()
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return float(100.0 - 100.0 / (1.0 + rs))


def _atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int) -> float:
    """Average True Range for most recent bar."""
    if len(close) < period + 1:
        return np.nan
    prev_close = close.shift(1)
    tr = pd.concat([
        high - low,
        (high - prev_close).abs(),
        (low - prev_close).abs(),
    ], axis=1).max(axis=1)
    return float(tr.iloc[-period:].mean())


def _returns(close: pd.Series, horizon: int) -> float:
    """Log return over *horizon* bars ending at the latest bar."""
    if len(close) <= horizon:
        return np.nan
    ret = float(np.log(close.iloc[-1] / close.iloc[-1 - horizon]))
    # MED-018: Sanity check — flag extreme returns (|return| > 50% per bar)
    if abs(ret) > 0.50:
        logger.warning(
            "Extreme return detected: %.4f over %d bars (close %.2f -> %.2f) — possible bad data",
            ret, horizon, close.iloc[-1 - horizon], close.iloc[-1],
        )
    return ret


# ---------------------------------------------------------------------------
# Feature Store
# ---------------------------------------------------------------------------

class FeatureStore:
    """Centralised feature computation and caching.

    Supports:
    - **Online store**: in-memory dict, refreshed every scan cycle.
    - **Offline store**: optional file/DB persistence for backtesting.
    - Thread-safe reads and writes.
    """

    # Default feature definitions — name -> (compute_fn, version, description, staleness_sec)
    _BUILTIN_FEATURES: list[tuple[str, int, str, float]] = [
        ("rsi_7", 1, "RSI with 7-bar lookback", 300),
        ("rsi_14", 1, "RSI with 14-bar lookback", 300),
        ("vwap_deviation", 1, "Price deviation from VWAP (%)", 120),
        ("atr_14", 1, "Average True Range (14-bar)", 300),
        ("bollinger_pct_b", 1, "Bollinger %B (20,2)", 300),
        ("bollinger_bandwidth", 1, "Bollinger Band width (20,2)", 300),
        ("volume_ratio", 1, "Current volume / 20-bar avg volume", 120),
        ("obv", 1, "On-Balance Volume (cumulative)", 300),
        ("money_flow_index", 1, "Money Flow Index (14-bar)", 300),
        ("return_1", 1, "1-bar log return", 120),
        ("return_5", 1, "5-bar log return", 120),
        ("return_20", 1, "20-bar log return", 300),
        ("return_60", 1, "60-bar log return", 600),
        ("volatility_realized", 1, "Realized vol (20-bar, annualised)", 300),
        ("volatility_parkinson", 1, "Parkinson vol (20-bar, annualised)", 300),
        ("volatility_garman_klass", 1, "Garman-Klass vol (20-bar, annualised)", 300),
        ("price_rel_ma_5", 1, "Price relative to 5-bar MA", 120),
        ("price_rel_ma_10", 1, "Price relative to 10-bar MA", 120),
        ("price_rel_ma_20", 1, "Price relative to 20-bar MA", 300),
        ("price_rel_ma_50", 1, "Price relative to 50-bar MA", 600),
        ("price_rel_ma_200", 1, "Price relative to 200-bar MA", 600),
    ]

    def __init__(self, offline_path: Optional[str] = None):
        self._lock = threading.Lock()

        # Online store: symbol -> {feature_name: value}
        self._online: Dict[str, Dict[str, float]] = {}
        # Timestamps: symbol -> {feature_name: epoch}
        self._timestamps: Dict[str, Dict[str, float]] = {}

        # Feature registry: name -> FeatureMeta
        self._registry: Dict[str, FeatureMeta] = {}

        # Offline path (parquet/sqlite for backtest snapshots)
        self._offline_path = offline_path

        # Stats
        self._compute_count = 0
        self._error_count = 0

        # MED-042: Track bar counts for incremental computation
        self._last_bar_count: Dict[str, int] = {}

        # PROD-003: Track last computed index per symbol for true incremental computation.
        # Maps symbol -> index (row count) of the last bar that was computed.
        # Only recomputes features when new bars arrive beyond this index.
        self._last_computed: Dict[str, int] = {}

        # Register built-in features
        self._register_builtins()

        logger.info("FeatureStore initialised with %d built-in features", len(self._registry))

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def _register_builtins(self):
        """Register all built-in feature definitions."""
        for name, version, desc, staleness in self._BUILTIN_FEATURES:
            meta = FeatureMeta(
                name=name, version=version,
                description=desc, staleness_threshold_sec=staleness,
            )
            self._registry[name] = meta


    @property
    def feature_names(self) -> List[str]:
        """Return list of all registered feature names."""
        with self._lock:
            return list(self._registry.keys())

    # ------------------------------------------------------------------
    # Core computation
    # ------------------------------------------------------------------


    def get_all_features(self, symbol: str) -> Dict[str, float]:
        """Return all cached features for a symbol (no recompute)."""
        with self._lock:
            return dict(self._online.get(symbol, {}))

    # ------------------------------------------------------------------
    # Offline persistence
    # ------------------------------------------------------------------


    def load_snapshot(self, timestamp: str) -> Dict[str, Dict[str, float]]:
        """Load a historical feature snapshot from offline storage.

        Args:
            timestamp: ISO timestamp label to load.

        Returns:
            Dict of symbol -> features, or empty dict on failure.
        """
        if not self._offline_path:
            return {}
        try:
            import os
            if not os.path.exists(self._offline_path):
                return {}

            df = pd.read_parquet(self._offline_path)
            snapshot = df[df["_snapshot_ts"] == timestamp]
            if snapshot.empty:
                return {}

            feature_cols = [c for c in snapshot.columns if c not in ("symbol", "_snapshot_ts")]
            result = {}
            for _, row in snapshot.iterrows():
                sym = row["symbol"]
                result[sym] = {col: float(row[col]) for col in feature_cols
                               if pd.notna(row[col])}
            return result
        except Exception as e:
            logger.error("FeatureStore: failed to load snapshot: %s", e)
            return {}

    # ------------------------------------------------------------------
    # Invalidation & stats
    # ------------------------------------------------------------------

    def invalidate(self, symbol: Optional[str] = None):
        """Clear cached features for a symbol, or all symbols if None."""
        with self._lock:
            if symbol:
                self._online.pop(symbol, None)
                self._timestamps.pop(symbol, None)
                self._last_computed.pop(symbol, None)
            else:
                self._online.clear()
                self._timestamps.clear()
                self._last_computed.clear()

    def stats(self) -> dict:
        """Return feature store statistics."""
        with self._lock:
            return {
                "registered_features": len(self._registry),
                "symbols_cached": len(self._online),
                "total_computes": self._compute_count,
                "total_errors": self._error_count,
                "offline_path": self._offline_path,
            }


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

_feature_store: Optional[FeatureStore] = None
_init_lock = threading.Lock()


def get_feature_store(offline_path: Optional[str] = None) -> FeatureStore:
    """Get or create the global FeatureStore singleton."""
    global _feature_store
    with _init_lock:
        if _feature_store is None:
            _feature_store = FeatureStore(offline_path=offline_path)
    return _feature_store

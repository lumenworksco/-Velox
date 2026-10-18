"""V8: Multi-timeframe confluence filter.

Checks alignment across daily, hourly, and 15-min timeframes.
- Breakout strategies (ORB, MICRO_MOM): need trend alignment (confluence >= 0.66)
- Mean reversion strategies (STAT_MR, VWAP): want dislocation (confluence <= 0.33)
"""

import logging
import threading
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

import config

logger = logging.getLogger(__name__)

# Cache to avoid refetching (thread-safe)
_mtf_lock = threading.Lock()
_mtf_cache: dict[str, tuple[float, datetime]] = {}


def clear_cache():
    """Clear the MTF cache."""
    global _mtf_cache
    with _mtf_lock:
        _mtf_cache = {}

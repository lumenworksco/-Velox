"""Tests for V8 Multi-Timeframe Confluence Filter."""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
from zoneinfo import ZoneInfo
import pandas as pd
import numpy as np

ET = ZoneInfo("America/New_York")


class TestMTFConfluence:

    def setup_method(self):
        """Clear cache before each test."""
        from analytics.mtf_confluence import clear_cache
        clear_cache()


    def test_clear_cache(self):
        from analytics.mtf_confluence import _mtf_cache, clear_cache
        _mtf_cache["test"] = (0.5, datetime.now())
        clear_cache()
        from analytics import mtf_confluence
        assert len(mtf_confluence._mtf_cache) == 0

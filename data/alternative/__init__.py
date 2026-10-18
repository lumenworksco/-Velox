"""Alternative data package — competitive edge data sources .

Provides modules for:
    - SEC EDGAR filing analysis (sec_filings)
    - Unusual options activity detection (options_flow)

All modules follow fail-open design: if data is unavailable, they return
neutral defaults and never block trading.
"""

from data.alternative.sec_filings import SECFilingAnalyzer, EdgarMonitor
from data.alternative.options_flow import OptionsFlowDetector

__all__ = [
    "SECFilingAnalyzer",
    "EdgarMonitor",
    "OptionsFlowDetector",
]

"""Market data API endpoints"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import logging

from core import SimplifiedDataFetcher

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize data fetcher
data_fetcher = SimplifiedDataFetcher()


class Quote(BaseModel):
    """Real-time quote"""
    symbol: str
    price: float
    change: float
    change_percent: float
    volume: int
    high: Optional[float] = None
    low: Optional[float] = None
    bid: Optional[float] = None
    ask: Optional[float] = None
    timestamp: datetime


class OHLCV(BaseModel):
    """OHLCV bar data"""
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int


@router.get("/quote/{symbol}", response_model=Quote)
async def get_quote(symbol: str):
    """
    Get real-time quote for a symbol.

    Returns current price, change, volume, and bid/ask spread.
    """
    try:
        data = data_fetcher.fetch_realtime_price(symbol)

        if data is None:
            raise HTTPException(status_code=404, detail=f"Symbol {symbol} not found")

        return Quote(
            symbol=symbol,
            price=data['price'],
            change=data['change'],
            change_percent=data['change_percent'],
            volume=data['volume'],
            bid=data.get('bid'),
            ask=data.get('ask'),
            timestamp=data['timestamp']
        )

    except Exception as e:
        logger.error(f"Error fetching quote for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/quotes", response_model=List[Quote])
async def get_quotes(symbols: List[str] = Query(...)):
    """
    Get real-time quotes for multiple symbols.

    **Example**: /api/market/quotes?symbols=AAPL&symbols=MSFT&symbols=GOOGL
    """
    try:
        # Use the parallel fetching method
        data_dict = data_fetcher.fetch_multiple_realtime(symbols)

        quotes = []
        for symbol, data in data_dict.items():
            if data:
                quotes.append(Quote(
                    symbol=symbol,
                    price=data['price'],
                    change=data['change'],
                    change_percent=data['change_percent'],
                    volume=data['volume'],
                    high=data.get('high'),
                    low=data.get('low'),
                    bid=data.get('bid'),
                    ask=data.get('ask'),
                    timestamp=data['timestamp']
                ))

        return quotes

    except Exception as e:
        logger.error(f"Error fetching quotes: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{symbol}", response_model=List[OHLCV])
async def get_history(
    symbol: str,
    timeframe: str = "1D",
    limit: int = 100
):
    """
    Get historical OHLCV data for a symbol.

    **Timeframes**: 1Min, 5Min, 15Min, 1H, 1D
    """
    try:
        # Map timeframe to yfinance parameters
        interval_map = {
            "1Min": "1m",
            "5Min": "5m",
            "15Min": "15m",
            "1H": "1h",
            "1D": "1d"
        }

        period_map = {
            "1m": "1d",   # 1 minute data only available for last day
            "5m": "5d",   # 5 minute data for last 5 days
            "15m": "1mo", # 15 minute data for last month
            "1h": "3mo",  # 1 hour data for last 3 months
            "1d": "1y"    # 1 day data for last year
        }

        interval = interval_map.get(timeframe, "1d")
        period = period_map.get(interval, "3mo")

        # Fetch historical data
        df = data_fetcher.fetch_data(symbol, period=period, interval=interval)

        if df is None or df.empty:
            raise HTTPException(status_code=404, detail=f"No historical data for {symbol}")

        # Convert to OHLCV format
        bars = []
        for idx, row in df.tail(limit).iterrows():
            bars.append(OHLCV(
                timestamp=idx,
                open=row['open'],
                high=row['high'],
                low=row['low'],
                close=row['close'],
                volume=int(row.get('volume', 0))
            ))

        return bars

    except Exception as e:
        logger.error(f"Error fetching history for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search")
async def search_symbols(query: str):
    """
    Search for symbols by name or ticker.

    Returns list of matching symbols.
    """
    # Simple mock search - in production, integrate with Alpaca assets API
    common_symbols = [
        {"symbol": "AAPL", "name": "Apple Inc.", "exchange": "NASDAQ"},
        {"symbol": "MSFT", "name": "Microsoft Corporation", "exchange": "NASDAQ"},
        {"symbol": "GOOGL", "name": "Alphabet Inc.", "exchange": "NASDAQ"},
        {"symbol": "AMZN", "name": "Amazon.com Inc.", "exchange": "NASDAQ"},
        {"symbol": "TSLA", "name": "Tesla Inc.", "exchange": "NASDAQ"},
        {"symbol": "META", "name": "Meta Platforms Inc.", "exchange": "NASDAQ"},
        {"symbol": "NVDA", "name": "NVIDIA Corporation", "exchange": "NASDAQ"},
        {"symbol": "SPY", "name": "SPDR S&P 500 ETF", "exchange": "NYSE"},
    ]

    query_lower = query.lower()
    results = [
        s for s in common_symbols
        if query_lower in s['symbol'].lower() or query_lower in s['name'].lower()
    ]

    return results[:10]  # Limit to 10 results

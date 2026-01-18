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
        data = data_fetcher.fetch_symbol(symbol)

        if data is None:
            raise HTTPException(status_code=404, detail=f"Symbol {symbol} not found")

        current_price = data['current_price']
        prev_close = data.get('prev_close', current_price)
        change = current_price - prev_close
        change_percent = (change / prev_close * 100) if prev_close != 0 else 0

        return Quote(
            symbol=symbol,
            price=current_price,
            change=change,
            change_percent=change_percent,
            volume=data.get('volume', 0),
            bid=data.get('bid'),
            ask=data.get('ask'),
            timestamp=datetime.now()
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
        quotes = []

        for symbol in symbols:
            try:
                data = data_fetcher.fetch_symbol(symbol)
                if data:
                    current_price = data['current_price']
                    prev_close = data.get('prev_close', current_price)
                    change = current_price - prev_close
                    change_percent = (change / prev_close * 100) if prev_close != 0 else 0

                    quotes.append(Quote(
                        symbol=symbol,
                        price=current_price,
                        change=change,
                        change_percent=change_percent,
                        volume=data.get('volume', 0),
                        bid=data.get('bid'),
                        ask=data.get('ask'),
                        timestamp=datetime.now()
                    ))
            except Exception as e:
                logger.error(f"Error fetching {symbol}: {e}")
                continue

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
        # Fetch historical data
        data = data_fetcher.fetch_symbol(symbol)

        if data is None or 'data' not in data:
            raise HTTPException(status_code=404, detail=f"No historical data for {symbol}")

        df = data['data']

        # Convert to OHLCV format
        bars = []
        for idx, row in df.tail(limit).iterrows():
            bars.append(OHLCV(
                timestamp=idx,
                open=row['open'],
                high=row['high'],
                low=row['low'],
                close=row['close'],
                volume=row.get('volume', 0)
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

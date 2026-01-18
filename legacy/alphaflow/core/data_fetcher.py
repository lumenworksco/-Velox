"""Data fetching module for Version 6 Trading App."""

import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

from .config import YF_AVAILABLE, ALPACA_AVAILABLE

if YF_AVAILABLE:
    import yfinance as yf


class SimplifiedDataFetcher:
    """Simplified data fetcher using yfinance."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.cache = {}
        self.cache_expiry = {}
        self.cache_duration = 60  # seconds
    
    def fetch_data(self, symbol: str, period: str = "3mo", 
                   interval: str = "1d") -> Optional[pd.DataFrame]:
        """Fetch historical data for a symbol."""
        
        cache_key = f"{symbol}_{period}_{interval}"
        
        # Check cache
        if cache_key in self.cache:
            if datetime.now().timestamp() < self.cache_expiry.get(cache_key, 0):
                return self.cache[cache_key].copy()
        
        if not YF_AVAILABLE:
            self.logger.warning("yfinance not available, generating sample data")
            return self._generate_sample_data(symbol, period)
        
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period, interval=interval)
            
            if data.empty:
                self.logger.warning(f"No data returned for {symbol}")
                return None
            
            # Standardize column names
            data.columns = [col.lower() for col in data.columns]
            
            # Store in cache
            self.cache[cache_key] = data.copy()
            self.cache_expiry[cache_key] = datetime.now().timestamp() + self.cache_duration
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error fetching data for {symbol}: {e}")
            return None
    
    def fetch_data_parallel(self, symbols: List[str], period: str = "3mo",
                           interval: str = "1d") -> Dict[str, pd.DataFrame]:
        """Fetch data for multiple symbols in parallel."""
        
        results = {}
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_symbol = {
                executor.submit(self.fetch_data, symbol, period, interval): symbol
                for symbol in symbols
            }
            
            for future in as_completed(future_to_symbol):
                symbol = future_to_symbol[future]
                try:
                    data = future.result()
                    if data is not None and len(data) > 0:
                        results[symbol] = data
                except Exception as e:
                    self.logger.error(f"Error fetching {symbol}: {e}")
        
        return results
    
    def fetch_realtime_price(self, symbol: str) -> Optional[Dict]:
        """Fetch real-time price data."""
        
        if not YF_AVAILABLE:
            return self._generate_sample_quote(symbol)
        
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            return {
                'symbol': symbol,
                'price': info.get('regularMarketPrice', info.get('previousClose', 0)),
                'change': info.get('regularMarketChange', 0),
                'change_percent': info.get('regularMarketChangePercent', 0),
                'volume': info.get('regularMarketVolume', 0),
                'high': info.get('regularMarketDayHigh', 0),
                'low': info.get('regularMarketDayLow', 0),
                'open': info.get('regularMarketOpen', 0),
                'previous_close': info.get('previousClose', 0),
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('trailingPE', 0),
                'dividend_yield': info.get('dividendYield', 0),
                'fifty_two_week_high': info.get('fiftyTwoWeekHigh', 0),
                'fifty_two_week_low': info.get('fiftyTwoWeekLow', 0),
                'timestamp': datetime.now()
            }
        except Exception as e:
            self.logger.error(f"Error fetching realtime price for {symbol}: {e}")
            return None
    
    def fetch_multiple_realtime(self, symbols: List[str]) -> Dict[str, Dict]:
        """Fetch real-time prices for multiple symbols."""
        
        results = {}
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_symbol = {
                executor.submit(self.fetch_realtime_price, symbol): symbol
                for symbol in symbols
            }
            
            for future in as_completed(future_to_symbol):
                symbol = future_to_symbol[future]
                try:
                    data = future.result()
                    if data is not None:
                        results[symbol] = data
                except Exception as e:
                    self.logger.error(f"Error fetching {symbol}: {e}")
        
        return results
    
    def _generate_sample_data(self, symbol: str, period: str = "3mo") -> pd.DataFrame:
        """Generate sample OHLCV data for testing."""
        
        periods_map = {
            '1mo': 22, '3mo': 66, '6mo': 132, '1y': 252, '2y': 504
        }
        num_days = periods_map.get(period, 66)
        
        dates = pd.date_range(end=datetime.now(), periods=num_days, freq='D')
        
        # Generate random walk price data
        np.random.seed(hash(symbol) % 2**32)
        base_price = np.random.uniform(50, 500)
        returns = np.random.normal(0.0005, 0.02, num_days)
        prices = base_price * np.cumprod(1 + returns)
        
        # Generate OHLCV
        data = pd.DataFrame({
            'open': prices * (1 + np.random.uniform(-0.01, 0.01, num_days)),
            'high': prices * (1 + np.random.uniform(0, 0.02, num_days)),
            'low': prices * (1 - np.random.uniform(0, 0.02, num_days)),
            'close': prices,
            'volume': np.random.uniform(1e6, 1e8, num_days).astype(int)
        }, index=dates)
        
        return data
    
    def _generate_sample_quote(self, symbol: str) -> Dict:
        """Generate sample quote data for testing."""
        
        np.random.seed(hash(symbol) % 2**32)
        price = np.random.uniform(50, 500)
        change = np.random.uniform(-5, 5)
        
        return {
            'symbol': symbol,
            'price': price,
            'change': change,
            'change_percent': (change / price) * 100,
            'volume': int(np.random.uniform(1e6, 1e8)),
            'high': price * 1.02,
            'low': price * 0.98,
            'open': price - change,
            'previous_close': price - change,
            'market_cap': int(price * np.random.uniform(1e9, 1e12)),
            'pe_ratio': np.random.uniform(10, 40),
            'dividend_yield': np.random.uniform(0, 0.03),
            'fifty_two_week_high': price * 1.3,
            'fifty_two_week_low': price * 0.7,
            'timestamp': datetime.now()
        }


class AlpacaDataFetcher:
    """Data fetcher using Alpaca API."""
    
    def __init__(self, api):
        self.api = api
        self.logger = logging.getLogger(__name__)
    
    def fetch_data(self, symbol: str, period: str = "3mo",
                   interval: str = "1d") -> Optional[pd.DataFrame]:
        """Fetch historical data from Alpaca."""
        
        try:
            period_days = {'1mo': 30, '3mo': 90, '6mo': 180, '1y': 365, '2y': 730}
            days = period_days.get(period, 90)
            
            end = datetime.now()
            start = end - timedelta(days=days)
            
            timeframe_map = {'1m': '1Min', '5m': '5Min', '15m': '15Min',
                           '1h': '1Hour', '1d': '1Day'}
            timeframe = timeframe_map.get(interval, '1Day')
            
            bars = self.api.get_bars(
                symbol,
                timeframe,
                start=start.isoformat(),
                end=end.isoformat()
            ).df
            
            if bars.empty:
                return None
            
            # Rename columns to match expected format
            bars.columns = [col.lower() for col in bars.columns]
            
            return bars
            
        except Exception as e:
            self.logger.error(f"Error fetching Alpaca data for {symbol}: {e}")
            # Fall back to yfinance
            fallback = SimplifiedDataFetcher()
            return fallback.fetch_data(symbol, period, interval)
    
    def fetch_data_parallel(self, symbols: List[str], period: str = "3mo",
                           interval: str = "1d") -> Dict[str, pd.DataFrame]:
        """Fetch data for multiple symbols."""
        
        results = {}
        for symbol in symbols:
            data = self.fetch_data(symbol, period, interval)
            if data is not None:
                results[symbol] = data
        return results


# Alias for backward compatibility
DataFetcher = SimplifiedDataFetcher

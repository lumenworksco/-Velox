"""Data controller for managing market data fetching and caching."""

import logging
from typing import Dict, List, Optional, Callable
from datetime import datetime, timedelta
from PyQt6.QtCore import QObject, pyqtSignal, QThread, QTimer

from core import (
    SimplifiedDataFetcher, AlpacaDataFetcher, AdvancedIndicators,
    ALPACA_AVAILABLE, YF_AVAILABLE
)
from .websocket_stream import WebSocketStreamManager


class DataFetchWorker(QThread):
    """Background worker for fetching market data."""

    data_ready = pyqtSignal(str, dict)  # symbol, data
    error = pyqtSignal(str, str)  # symbol, error_message
    progress = pyqtSignal(int)  # progress percentage

    def __init__(self, symbols: List[str], use_alpaca: bool = False):
        super().__init__()
        self.symbols = symbols
        self.use_alpaca = use_alpaca
        self.is_running = True

    def run(self):
        """Fetch data for all symbols."""
        # Create appropriate data fetcher
        # For now, use SimplifiedDataFetcher (yfinance) as it doesn't need API credentials
        # TODO: Add proper Alpaca API integration with credential management
        if YF_AVAILABLE:
            fetcher = SimplifiedDataFetcher()
        else:
            self.error.emit("ALL", "No data fetcher available (yfinance not installed)")
            return

        total = len(self.symbols)

        for i, symbol in enumerate(self.symbols):
            if not self.is_running:
                break

            try:
                # Fetch historical data
                df = fetcher.fetch_data(symbol, period='3mo')

                if df is not None and len(df) > 0:
                    # Calculate indicators
                    df = AdvancedIndicators.calculate_all_indicators(df)

                    # Get current quote
                    quote = fetcher.fetch_realtime_price(symbol)

                    data = {
                        'historical': df,
                        'quote': quote,
                        'timestamp': datetime.now()
                    }

                    self.data_ready.emit(symbol, data)
                else:
                    self.error.emit(symbol, "No data available")

            except Exception as e:
                self.error.emit(symbol, str(e))

            # Update progress
            self.progress.emit(int((i + 1) / total * 100))

    def stop(self):
        """Stop the worker."""
        self.is_running = False


class DataController(QObject):
    """
    Controller for managing market data fetching, caching, and updates.

    Responsibilities:
    - Fetch market data from Alpaca or yfinance
    - Cache data to reduce API calls
    - Provide real-time quote updates
    - Manage background data refresh
    """

    data_updated = pyqtSignal(str, dict)  # symbol, data
    batch_update_complete = pyqtSignal(dict)  # all_data
    error_occurred = pyqtSignal(str, str)  # symbol, error_message
    fetch_progress = pyqtSignal(int)  # progress percentage
    realtime_quote_updated = pyqtSignal(str, dict)  # symbol, quote (real-time from WebSocket)

    def __init__(self, use_alpaca: bool = True, enable_streaming: bool = False):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.use_alpaca = use_alpaca and ALPACA_AVAILABLE
        self.enable_streaming = enable_streaming

        # Data cache
        self.cache: Dict[str, dict] = {}
        self.cache_timeout = timedelta(minutes=5)

        # Workers
        self.fetch_worker: Optional[DataFetchWorker] = None

        # WebSocket streaming
        self.stream_manager: Optional[WebSocketStreamManager] = None
        if self.enable_streaming and self.use_alpaca:
            self.stream_manager = WebSocketStreamManager(use_paper=True)
            self.stream_manager.quote_updated.connect(self._on_realtime_quote)
            self.stream_manager.trade_updated.connect(self._on_realtime_trade)
            self.stream_manager.error_occurred.connect(self._on_stream_error)

        # Auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self._auto_refresh)
        self.refresh_interval = 60000  # 60 seconds

        # Watchlist
        self.watchlist: List[str] = []

    def set_watchlist(self, symbols: List[str]):
        """
        Set the watchlist symbols.

        Args:
            symbols: List of stock symbols
        """
        self.watchlist = symbols
        self.logger.info(f"Watchlist updated: {symbols}")

        # Start streaming for watchlist if enabled
        if self.stream_manager and self.enable_streaming:
            self.stream_manager.start_stream(symbols)

    def fetch_symbols(self, symbols: List[str], callback: Optional[Callable] = None):
        """
        Fetch data for multiple symbols.

        Args:
            symbols: List of stock symbols to fetch
            callback: Optional callback function when complete
        """
        if self.fetch_worker and self.fetch_worker.isRunning():
            self.logger.warning("Previous fetch still running, stopping it")
            self.fetch_worker.stop()
            self.fetch_worker.wait()

        # Create new worker
        self.fetch_worker = DataFetchWorker(symbols, self.use_alpaca)
        self.fetch_worker.data_ready.connect(self._on_data_ready)
        self.fetch_worker.error.connect(self._on_fetch_error)
        self.fetch_worker.progress.connect(self.fetch_progress.emit)

        if callback:
            self.fetch_worker.finished.connect(callback)

        self.fetch_worker.start()

    def fetch_symbol(self, symbol: str) -> Optional[dict]:
        """
        Fetch data for a single symbol (synchronous).

        Args:
            symbol: Stock symbol

        Returns:
            Data dictionary or None if failed
        """
        # Check cache first
        if symbol in self.cache:
            cached_data = self.cache[symbol]
            cache_age = datetime.now() - cached_data['timestamp']

            if cache_age < self.cache_timeout:
                self.logger.debug(f"Using cached data for {symbol}")
                return cached_data

        # Fetch fresh data
        try:
            # Use SimplifiedDataFetcher for now (yfinance)
            fetcher = SimplifiedDataFetcher()

            df = fetcher.fetch_data(symbol, period='3mo')

            if df is not None and len(df) > 0:
                df = AdvancedIndicators.calculate_all_indicators(df)
                quote = fetcher.fetch_realtime_price(symbol)

                data = {
                    'historical': df,
                    'quote': quote,
                    'timestamp': datetime.now()
                }

                self.cache[symbol] = data
                return data

        except Exception as e:
            self.logger.error(f"Error fetching {symbol}: {e}")
            self.error_occurred.emit(symbol, str(e))

        return None

    def get_cached_data(self, symbol: str) -> Optional[dict]:
        """
        Get cached data for a symbol.

        Args:
            symbol: Stock symbol

        Returns:
            Cached data or None
        """
        return self.cache.get(symbol)

    def start_auto_refresh(self, interval_ms: int = 60000):
        """
        Start automatic data refresh.

        Args:
            interval_ms: Refresh interval in milliseconds (default 60 seconds)
        """
        self.refresh_interval = interval_ms
        self.refresh_timer.start(interval_ms)
        self.logger.info(f"Auto-refresh started: {interval_ms}ms interval")

    def stop_auto_refresh(self):
        """Stop automatic data refresh."""
        self.refresh_timer.stop()
        self.logger.info("Auto-refresh stopped")

    def _auto_refresh(self):
        """Automatically refresh watchlist data."""
        if self.watchlist:
            self.logger.debug("Auto-refreshing watchlist data")
            self.fetch_symbols(self.watchlist)

    def _on_data_ready(self, symbol: str, data: dict):
        """Handle data ready from worker."""
        self.cache[symbol] = data
        self.data_updated.emit(symbol, data)

    def _on_fetch_error(self, symbol: str, error: str):
        """Handle fetch error from worker."""
        self.logger.error(f"Error fetching {symbol}: {error}")
        self.error_occurred.emit(symbol, error)

    def clear_cache(self):
        """Clear the data cache."""
        self.cache.clear()
        self.logger.info("Data cache cleared")

    def _on_realtime_quote(self, symbol: str, quote_data: dict):
        """
        Handle real-time quote update from WebSocket.

        Args:
            symbol: Stock symbol
            quote_data: Quote data dictionary
        """
        self.logger.debug(f"Real-time quote: {symbol} - Bid: {quote_data.get('bid')}, Ask: {quote_data.get('ask')}")

        # Update cache with latest quote
        if symbol in self.cache:
            # Calculate mid-price
            bid = quote_data.get('bid', 0)
            ask = quote_data.get('ask', 0)
            mid_price = (bid + ask) / 2 if bid > 0 and ask > 0 else 0

            # Update cached quote
            cached_data = self.cache[symbol]
            if 'quote' in cached_data:
                old_price = cached_data['quote'].get('price', 0)
                change = mid_price - old_price if old_price > 0 else 0
                change_pct = (change / old_price * 100) if old_price > 0 else 0

                cached_data['quote'].update({
                    'price': mid_price,
                    'bid': bid,
                    'ask': ask,
                    'change': change,
                    'change_percent': change_pct
                })

        # Emit real-time quote signal
        self.realtime_quote_updated.emit(symbol, quote_data)

    def _on_realtime_trade(self, symbol: str, trade_data: dict):
        """
        Handle real-time trade update from WebSocket.

        Args:
            symbol: Stock symbol
            trade_data: Trade data dictionary
        """
        self.logger.debug(f"Real-time trade: {symbol} - Price: {trade_data.get('price')}, Size: {trade_data.get('size')}")

        # Update cache with latest trade price
        if symbol in self.cache:
            cached_data = self.cache[symbol]
            if 'quote' in cached_data:
                price = trade_data.get('price', 0)
                old_price = cached_data['quote'].get('price', 0)
                change = price - old_price if old_price > 0 else 0
                change_pct = (change / old_price * 100) if old_price > 0 else 0

                cached_data['quote'].update({
                    'price': price,
                    'change': change,
                    'change_percent': change_pct
                })

                # Emit update
                self.data_updated.emit(symbol, cached_data)

    def _on_stream_error(self, error: str):
        """Handle streaming error."""
        self.logger.error(f"Streaming error: {error}")
        self.error_occurred.emit("STREAM", error)

    def enable_realtime_streaming(self, enable: bool = True):
        """
        Enable or disable real-time WebSocket streaming.

        Args:
            enable: True to enable streaming, False to disable
        """
        self.enable_streaming = enable

        if enable and not self.stream_manager:
            self.stream_manager = WebSocketStreamManager(use_paper=True)
            self.stream_manager.quote_updated.connect(self._on_realtime_quote)
            self.stream_manager.trade_updated.connect(self._on_realtime_trade)
            self.stream_manager.error_occurred.connect(self._on_stream_error)

            if self.watchlist:
                self.stream_manager.start_stream(self.watchlist)
        elif not enable and self.stream_manager:
            self.stream_manager.stop_stream()

    def cleanup(self):
        """Clean up resources."""
        self.stop_auto_refresh()

        if self.fetch_worker and self.fetch_worker.isRunning():
            self.fetch_worker.stop()
            self.fetch_worker.wait()

        if self.stream_manager:
            self.stream_manager.cleanup()

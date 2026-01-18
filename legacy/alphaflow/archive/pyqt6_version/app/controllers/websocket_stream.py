"""WebSocket streaming for real-time market data."""

import logging
import os
from typing import List, Optional, Callable
from PyQt6.QtCore import QObject, pyqtSignal, QThread

try:
    from alpaca_trade_api.stream import Stream
    from alpaca_trade_api.common import URL
    ALPACA_WS_AVAILABLE = True
except ImportError:
    ALPACA_WS_AVAILABLE = False


class WebSocketStreamWorker(QThread):
    """Background worker for Alpaca WebSocket streaming."""

    quote_received = pyqtSignal(str, dict)  # symbol, quote_data
    trade_received = pyqtSignal(str, dict)  # symbol, trade_data
    error_occurred = pyqtSignal(str)  # error_message
    connected = pyqtSignal()
    disconnected = pyqtSignal()

    def __init__(self, symbols: List[str], use_paper: bool = True):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.symbols = symbols
        self.use_paper = use_paper
        self.stream: Optional[Stream] = None
        self.is_running = True

        # Get API credentials from environment
        self.api_key = os.getenv('ALPACA_API_KEY')
        self.secret_key = os.getenv('ALPACA_SECRET_KEY')

    def run(self):
        """Start WebSocket streaming."""
        if not ALPACA_WS_AVAILABLE:
            self.error_occurred.emit("Alpaca WebSocket not available (alpaca-trade-api not installed)")
            return

        if not self.api_key or not self.secret_key:
            self.error_occurred.emit("Alpaca API credentials not configured")
            return

        try:
            # Create stream connection
            base_url = 'https://paper-api.alpaca.markets' if self.use_paper else 'https://api.alpaca.markets'

            self.stream = Stream(
                self.api_key,
                self.secret_key,
                base_url=URL(base_url),
                data_feed='iex'  # Use IEX data feed
            )

            # Subscribe to quotes
            for symbol in self.symbols:
                self.stream.subscribe_quotes(self._on_quote, symbol)
                self.stream.subscribe_trades(self._on_trade, symbol)

            self.logger.info(f"WebSocket stream starting for symbols: {self.symbols}")
            self.connected.emit()

            # Run the stream (blocking)
            self.stream.run()

        except Exception as e:
            self.logger.error(f"WebSocket streaming error: {e}")
            self.error_occurred.emit(str(e))
        finally:
            self.disconnected.emit()

    def _on_quote(self, quote):
        """Handle incoming quote update."""
        try:
            symbol = quote.symbol
            quote_data = {
                'bid': float(quote.bid_price) if quote.bid_price else 0.0,
                'ask': float(quote.ask_price) if quote.ask_price else 0.0,
                'bid_size': int(quote.bid_size) if quote.bid_size else 0,
                'ask_size': int(quote.ask_size) if quote.ask_size else 0,
                'timestamp': quote.timestamp
            }
            self.quote_received.emit(symbol, quote_data)
        except Exception as e:
            self.logger.error(f"Error processing quote: {e}")

    def _on_trade(self, trade):
        """Handle incoming trade update."""
        try:
            symbol = trade.symbol
            trade_data = {
                'price': float(trade.price),
                'size': int(trade.size),
                'timestamp': trade.timestamp
            }
            self.trade_received.emit(symbol, trade_data)
        except Exception as e:
            self.logger.error(f"Error processing trade: {e}")

    def stop(self):
        """Stop the WebSocket stream."""
        self.is_running = False
        if self.stream:
            try:
                self.stream.stop()
            except Exception as e:
                self.logger.error(f"Error stopping stream: {e}")


class WebSocketStreamManager(QObject):
    """
    Manager for WebSocket streaming connections.

    Provides real-time market data via Alpaca WebSocket.
    """

    quote_updated = pyqtSignal(str, dict)  # symbol, quote_data
    trade_updated = pyqtSignal(str, dict)  # symbol, trade_data
    connection_status_changed = pyqtSignal(bool)  # connected/disconnected
    error_occurred = pyqtSignal(str)  # error_message

    def __init__(self, use_paper: bool = True):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.use_paper = use_paper

        self.worker: Optional[WebSocketStreamWorker] = None
        self.subscribed_symbols: List[str] = []

    def start_stream(self, symbols: List[str]):
        """
        Start WebSocket streaming for the given symbols.

        Args:
            symbols: List of stock symbols to stream
        """
        if self.worker and self.worker.isRunning():
            self.logger.warning("WebSocket stream already running, stopping it first")
            self.stop_stream()

        self.subscribed_symbols = symbols

        # Create and start worker
        self.worker = WebSocketStreamWorker(symbols, self.use_paper)
        self.worker.quote_received.connect(self._on_quote_received)
        self.worker.trade_received.connect(self._on_trade_received)
        self.worker.connected.connect(lambda: self.connection_status_changed.emit(True))
        self.worker.disconnected.connect(lambda: self.connection_status_changed.emit(False))
        self.worker.error_occurred.connect(self._on_error)

        self.worker.start()
        self.logger.info(f"Started WebSocket stream for {len(symbols)} symbols")

    def stop_stream(self):
        """Stop the WebSocket stream."""
        if self.worker:
            self.worker.stop()
            self.worker.wait(1000)  # Wait up to 1 second
            self.worker = None
            self.logger.info("Stopped WebSocket stream")

    def add_symbol(self, symbol: str):
        """
        Add a symbol to the stream.

        Args:
            symbol: Stock symbol to add
        """
        if symbol not in self.subscribed_symbols:
            self.subscribed_symbols.append(symbol)

            # Restart stream with new symbols
            if self.worker and self.worker.isRunning():
                self.start_stream(self.subscribed_symbols)

    def remove_symbol(self, symbol: str):
        """
        Remove a symbol from the stream.

        Args:
            symbol: Stock symbol to remove
        """
        if symbol in self.subscribed_symbols:
            self.subscribed_symbols.remove(symbol)

            # Restart stream with remaining symbols
            if self.worker and self.worker.isRunning() and self.subscribed_symbols:
                self.start_stream(self.subscribed_symbols)
            elif not self.subscribed_symbols:
                self.stop_stream()

    def _on_quote_received(self, symbol: str, quote_data: dict):
        """Handle quote received from worker."""
        self.quote_updated.emit(symbol, quote_data)

    def _on_trade_received(self, symbol: str, trade_data: dict):
        """Handle trade received from worker."""
        self.trade_updated.emit(symbol, trade_data)

    def _on_error(self, error: str):
        """Handle error from worker."""
        self.logger.error(f"WebSocket error: {error}")
        self.error_occurred.emit(error)

    def is_connected(self) -> bool:
        """Check if WebSocket is currently connected."""
        return self.worker is not None and self.worker.isRunning()

    def cleanup(self):
        """Clean up resources."""
        self.stop_stream()

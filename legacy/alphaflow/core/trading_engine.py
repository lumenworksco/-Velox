"""Trading Engine for Version 6 Trading App."""

import time
import logging
from datetime import datetime
from typing import List, Dict, Optional
import pandas as pd

from .config import (
    ALPACA_AVAILABLE, setup_logging, TradingConfig,
    is_market_open, get_market_status_message
)
from .data_fetcher import SimplifiedDataFetcher, AlpacaDataFetcher
from .indicators import AdvancedIndicators
from .ml_predictor import MLPredictor
from .strategies import TradingStrategies
from .risk_manager import RiskManager
from .portfolio_manager import PortfolioManager
from .data_structures import TradeSignal, SignalAction

if ALPACA_AVAILABLE:
    from alpaca_trade_api import REST


class TradingEngine:
    """Main trading engine for Version 6."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        paper: bool = True,
        initial_capital: float = 100000
    ):
        """Initialize the trading engine."""

        setup_logging()
        self.logger = logging.getLogger(__name__)

        self.api_key = api_key
        self.secret_key = secret_key
        self.paper = paper
        self.initial_capital = initial_capital

        # Initialize Alpaca API if credentials provided
        self.api = None
        if api_key and secret_key and ALPACA_AVAILABLE:
            try:
                base_url = 'https://paper-api.alpaca.markets' if paper else 'https://api.alpaca.markets'
                self.api = REST(api_key, secret_key, base_url, api_version='v2')

                # Get account info
                account = self.api.get_account()
                self.logger.info(f"✅ Connected to Alpaca ({'Paper' if paper else 'Live'} Trading)")
                self.logger.info(f"   Account: ${float(account.cash):,.2f} cash")
            except Exception as e:
                self.logger.error(f"❌ Failed to connect to Alpaca: {e}")
                self.api = None

        # Initialize components
        if self.api:
            self.data_fetcher = AlpacaDataFetcher(self.api)
        else:
            self.data_fetcher = SimplifiedDataFetcher()

        self.ml_predictor = MLPredictor()
        self.strategies = TradingStrategies(self.ml_predictor)
        self.risk_manager = RiskManager(initial_capital)
        self.portfolio_manager = PortfolioManager(initial_capital)

        # Sync with Alpaca account if connected
        if self.api:
            try:
                account = self.api.get_account()
                self.portfolio_manager.sync_with_alpaca_account(float(account.cash))
            except Exception as e:
                self.logger.warning(f"Could not sync with Alpaca account: {e}")

        self.is_running = False
        self.current_signals = []

        self.logger.info("🚀 Trading Engine initialized")
        self.logger.info(f"   Initial Capital: ${initial_capital:,.2f}")
        self.logger.info(f"   Mode: {'Live API' if self.api else 'Simulation'}")

    def analyze_symbol(self, symbol: str) -> Dict:
        """Analyze a single symbol and return analysis results."""

        result = {
            'symbol': symbol,
            'success': False,
            'data': None,
            'indicators': {},
            'signals': [],
            'trend': 'UNKNOWN',
            'momentum': 0,
            'volatility': 'MEDIUM',
            'ml_prediction': None,
            'error': None
        }

        try:
            # Fetch data
            data = self.data_fetcher.fetch_data(symbol, period='3mo')

            if data is None or len(data) < 50:
                result['error'] = "Insufficient data"
                return result

            # Calculate indicators
            data_with_indicators = AdvancedIndicators.calculate_all_indicators(data)
            result['data'] = data_with_indicators

            # Get trend, momentum, volatility
            result['trend'] = AdvancedIndicators.get_trend_direction(data_with_indicators)
            result['momentum'] = AdvancedIndicators.get_momentum_score(data_with_indicators)
            result['volatility'] = AdvancedIndicators.get_volatility_level(data_with_indicators)

            # Extract key indicators
            latest = data_with_indicators.iloc[-1]
            result['indicators'] = {
                'price': latest['close'],
                'rsi': latest.get('rsi', 50),
                'macd': latest.get('macd', 0),
                'macd_signal': latest.get('macd_signal', 0),
                'bb_percent': latest.get('bb_percent', 0.5),
                'stoch_k': latest.get('stoch_k', 50),
                'adx': latest.get('adx', 20),
                'atr': latest.get('atr', 0),
                'volume_ratio': latest.get('volume_ratio', 1)
            }

            # Train ML model if needed
            self.ml_predictor.retrain_if_needed(data_with_indicators)

            # Get ML prediction
            if self.ml_predictor.is_trained:
                result['ml_prediction'] = self.ml_predictor.predict(data_with_indicators)

            # Generate signals
            signals = self.strategies.generate_all_signals(data_with_indicators, symbol)
            result['signals'] = signals

            result['success'] = True

        except Exception as e:
            self.logger.error(f"Error analyzing {symbol}: {e}")
            result['error'] = str(e)

        return result

    def analyze_watchlist(self, symbols: List[str]) -> Dict[str, Dict]:
        """Analyze multiple symbols."""

        results = {}
        data_dict = self.data_fetcher.fetch_data_parallel(symbols)

        for symbol in symbols:
            if symbol in data_dict and data_dict[symbol] is not None:
                results[symbol] = self.analyze_symbol(symbol)
            else:
                results[symbol] = {
                    'symbol': symbol,
                    'success': False,
                    'error': 'Failed to fetch data'
                }

        return results

    def execute_signal(self, signal: TradeSignal) -> bool:
        """Execute a trading signal."""

        # Check risk limits
        risk_check = self.risk_manager.check_risk_limits(
            signal, list(self.portfolio_manager.positions.values())
        )

        if not risk_check['approved']:
            self.logger.warning(f"Signal rejected: {risk_check['reasons']}")
            return False

        # Calculate position size
        position_size = self.risk_manager.calculate_position_size(
            signal, signal.price
        )

        if position_size <= 0:
            self.logger.warning("Position size is 0")
            return False

        # Execute trade
        if signal.action in [SignalAction.BUY, SignalAction.STRONG_BUY]:
            if self.api:
                try:
                    self.api.submit_order(
                        symbol=signal.symbol,
                        qty=position_size,
                        side='buy',
                        type='market',
                        time_in_force='day'
                    )
                    self.logger.info(f"Order submitted: BUY {position_size} {signal.symbol}")
                except Exception as e:
                    self.logger.error(f"Order failed: {e}")
                    return False

            # Update portfolio
            self.portfolio_manager.add_position(
                signal.symbol, position_size, signal.price,
                signal.strategy, signal.stop_loss, signal.take_profit
            )
            return True

        elif signal.action in [SignalAction.SELL, SignalAction.STRONG_SELL]:
            if signal.symbol in self.portfolio_manager.positions:
                if self.api:
                    try:
                        position = self.portfolio_manager.positions[signal.symbol]
                        self.api.submit_order(
                            symbol=signal.symbol,
                            qty=position.quantity,
                            side='sell',
                            type='market',
                            time_in_force='day'
                        )
                    except Exception as e:
                        self.logger.error(f"Order failed: {e}")
                        return False

                # Update portfolio
                self.portfolio_manager.close_position(signal.symbol, signal.price)
                return True

        return False

    def update_portfolio_prices(self, symbols: List[str]):
        """Update current prices for all positions."""

        prices = {}
        for symbol in symbols:
            quote = self.data_fetcher.fetch_realtime_price(symbol)
            if quote:
                prices[symbol] = quote['price']

        self.portfolio_manager.update_prices(prices)

    def get_portfolio_summary(self) -> Dict:
        """Get current portfolio summary."""
        return self.portfolio_manager.get_summary()

    def get_risk_metrics(self) -> Dict:
        """Get current risk metrics."""
        return self.risk_manager.get_risk_metrics()

    def get_market_status(self) -> str:
        """Get market status message."""
        return get_market_status_message()

    def is_market_open(self) -> bool:
        """Check if market is open."""
        return is_market_open()

    # ========================================================================
    # Order Management Methods
    # ========================================================================

    def place_order(
        self,
        symbol: str,
        side: str,
        quantity: int,
        order_type: str = 'market',
        limit_price: Optional[float] = None,
        stop_price: Optional[float] = None
    ) -> Dict:
        """
        Place a trading order.

        Args:
            symbol: Stock symbol
            side: 'buy' or 'sell'
            quantity: Number of shares
            order_type: 'market', 'limit', or 'stop'
            limit_price: Limit price for limit orders
            stop_price: Stop price for stop orders

        Returns:
            Order information dictionary
        """
        if not self.api:
            raise Exception("Alpaca API not initialized. Please configure API keys.")

        try:
            # Prepare order parameters
            order_params = {
                'symbol': symbol,
                'qty': quantity,
                'side': side,
                'type': order_type,
                'time_in_force': 'day'
            }

            # Add price parameters for limit/stop orders
            if order_type == 'limit' and limit_price:
                order_params['limit_price'] = limit_price
            elif order_type == 'stop' and stop_price:
                order_params['stop_price'] = stop_price

            # Submit order to Alpaca
            order = self.api.submit_order(**order_params)

            self.logger.info(f"Order placed: {side.upper()} {quantity} {symbol} @ {order_type}")

            return {
                'id': order.id,
                'status': order.status,
                'symbol': order.symbol,
                'side': order.side,
                'quantity': int(order.qty),
                'filled_qty': int(order.filled_qty) if order.filled_qty else 0,
                'avg_price': float(order.filled_avg_price) if order.filled_avg_price else None,
                'created_at': order.created_at
            }

        except Exception as e:
            self.logger.error(f"Failed to place order: {e}")
            raise

    def get_orders(self, status: Optional[str] = None) -> List[Dict]:
        """
        Get orders, optionally filtered by status.

        Args:
            status: Filter by status ('open', 'closed', 'all')

        Returns:
            List of order dictionaries
        """
        if not self.api:
            return []

        try:
            # Get orders from Alpaca
            orders = self.api.list_orders(status=status or 'all', limit=100)

            return [
                {
                    'id': order.id,
                    'status': order.status,
                    'symbol': order.symbol,
                    'side': order.side,
                    'quantity': int(order.qty),
                    'filled_qty': int(order.filled_qty) if order.filled_qty else 0,
                    'avg_price': float(order.filled_avg_price) if order.filled_avg_price else None,
                    'created_at': order.created_at
                }
                for order in orders
            ]

        except Exception as e:
            self.logger.error(f"Failed to get orders: {e}")
            return []

    def cancel_order(self, order_id: str) -> Dict:
        """
        Cancel an open order.

        Args:
            order_id: Order ID to cancel

        Returns:
            Cancellation confirmation
        """
        if not self.api:
            raise Exception("Alpaca API not initialized. Please configure API keys.")

        try:
            self.api.cancel_order(order_id)
            self.logger.info(f"Order canceled: {order_id}")

            return {
                'success': True,
                'order_id': order_id,
                'status': 'canceled'
            }

        except Exception as e:
            self.logger.error(f"Failed to cancel order: {e}")
            raise

    def get_positions(self) -> List[Dict]:
        """
        Get all open positions.

        Returns:
            List of position dictionaries
        """
        if not self.api:
            return []

        try:
            # Get positions from Alpaca
            positions = self.api.list_positions()

            return [
                {
                    'symbol': pos.symbol,
                    'quantity': int(pos.qty),
                    'avg_entry_price': float(pos.avg_entry_price),
                    'current_price': float(pos.current_price),
                    'market_value': float(pos.market_value),
                    'unrealized_pnl': float(pos.unrealized_pl),
                    'unrealized_pnl_percent': float(pos.unrealized_plpc) * 100
                }
                for pos in positions
            ]

        except Exception as e:
            self.logger.error(f"Failed to get positions: {e}")
            return []

    def close_position(self, symbol: str) -> Dict:
        """
        Close an entire position.

        Args:
            symbol: Stock symbol to close

        Returns:
            Closure confirmation
        """
        if not self.api:
            raise Exception("Alpaca API not initialized. Please configure API keys.")

        try:
            # Close position via Alpaca
            self.api.close_position(symbol)
            self.logger.info(f"Position closed: {symbol}")

            # Update internal portfolio manager
            if symbol in self.portfolio_manager.positions:
                current_price = self.data_fetcher.fetch_realtime_price(symbol)
                if current_price:
                    self.portfolio_manager.close_position(symbol, current_price['price'])

            return {
                'success': True,
                'symbol': symbol,
                'message': f'Position closed for {symbol}'
            }

        except Exception as e:
            self.logger.error(f"Failed to close position: {e}")
            raise

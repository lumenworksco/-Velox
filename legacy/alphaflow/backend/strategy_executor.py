"""Strategy execution manager for running trading strategies"""

import asyncio
import logging
from typing import Dict, Optional
from datetime import datetime
import threading
import os

from core.trading_engine import TradingEngine
from core.data_fetcher import SimplifiedDataFetcher
from backend.strategy_logic import strategy_logic
from backend.position_manager import position_manager
from backend.daily_risk_manager import daily_risk_manager
from backend.trade_history import trade_history
from backend.notification_system import notification_system
from backend.portfolio_risk import portfolio_risk_manager

logger = logging.getLogger(__name__)


class StrategyExecutor:
    """Manages execution of trading strategies"""

    def __init__(self):
        self.running_strategies: Dict[str, dict] = {}
        self.execution_threads: Dict[str, threading.Thread] = {}
        self.stop_flags: Dict[str, threading.Event] = {}

        # Initialize trading engine (will use paper trading by default)
        # Get API keys from environment variables
        api_key = os.getenv('ALPACA_API_KEY')
        secret_key = os.getenv('ALPACA_SECRET_KEY')

        self.trading_engine = None
        if api_key and secret_key:
            try:
                self.trading_engine = TradingEngine(
                    api_key=api_key,
                    secret_key=secret_key,
                    paper=True,  # Start in paper mode by default
                    initial_capital=100000
                )
                logger.info("Trading engine initialized with Alpaca API")
            except Exception as e:
                logger.error(f"Failed to initialize trading engine: {e}")
        else:
            logger.warning("No Alpaca API keys found - strategies will run in simulation mode")

    def start_strategy(self, strategy_id: str, strategy_config: dict) -> bool:
        """Start executing a strategy"""
        try:
            if strategy_id in self.running_strategies:
                logger.warning(f"Strategy {strategy_id} is already running")
                return False

            # Create stop flag
            stop_flag = threading.Event()
            self.stop_flags[strategy_id] = stop_flag

            # Create execution thread
            thread = threading.Thread(
                target=self._execute_strategy,
                args=(strategy_id, strategy_config, stop_flag),
                daemon=True
            )

            self.execution_threads[strategy_id] = thread
            self.running_strategies[strategy_id] = {
                'start_time': datetime.now(),
                'config': strategy_config,
                'status': 'running'
            }

            thread.start()
            logger.info(f"Started strategy {strategy_id}")

            # Send notification
            notification_system.alert_strategy_started(
                strategy_id=strategy_id,
                symbols=strategy_config.get('symbols', [])
            )

            return True

        except Exception as e:
            logger.error(f"Failed to start strategy {strategy_id}: {e}")
            return False

    def stop_strategy(self, strategy_id: str) -> bool:
        """Stop a running strategy"""
        try:
            if strategy_id not in self.running_strategies:
                logger.warning(f"Strategy {strategy_id} is not running")
                return False

            # Set stop flag
            if strategy_id in self.stop_flags:
                self.stop_flags[strategy_id].set()

            # Wait for thread to finish (with timeout)
            if strategy_id in self.execution_threads:
                thread = self.execution_threads[strategy_id]
                thread.join(timeout=5.0)

            # Clean up
            self.running_strategies.pop(strategy_id, None)
            self.execution_threads.pop(strategy_id, None)
            self.stop_flags.pop(strategy_id, None)

            logger.info(f"Stopped strategy {strategy_id}")

            # Send notification
            notification_system.alert_strategy_stopped(
                strategy_id=strategy_id,
                reason="User request"
            )

            return True

        except Exception as e:
            logger.error(f"Failed to stop strategy {strategy_id}: {e}")
            return False

    def _execute_strategy(self, strategy_id: str, config: dict, stop_flag: threading.Event):
        """Execute strategy in background thread"""
        try:
            logger.info(f"Executing strategy {strategy_id} with config: {config}")

            # Initialize components
            data_fetcher = SimplifiedDataFetcher()

            # Extract configuration
            symbols = config.get('symbols', [])
            parameters = config.get('parameters', {})
            strategy_name = config.get('name', 'Unknown Strategy')

            # Main execution loop
            while not stop_flag.is_set():
                try:
                    # Check daily risk limits
                    can_trade, reason = daily_risk_manager.can_trade()
                    if not can_trade:
                        logger.warning(f"Strategy {strategy_id}: Trading halted - {reason}")
                        stop_flag.wait(timeout=300)  # Wait 5 minutes before checking again
                        continue

                    # Fetch latest data for symbols
                    for symbol in symbols:
                        if stop_flag.is_set():
                            break

                        # Fetch recent data
                        data = data_fetcher.fetch_data(symbol, period='1d')

                        if data is not None and len(data) > 0:
                            current_price = data['close'].iloc[-1]
                            logger.debug(f"Strategy {strategy_id}: Processing {symbol}, latest price: ${current_price:.2f}")

                            # Generate trading signal
                            signal = strategy_logic.generate_signal(
                                strategy_id=strategy_id,
                                symbol=symbol,
                                data=data,
                                parameters=parameters
                            )

                            # Execute trades based on signal
                            if signal == 'BUY':
                                # Only buy if we don't already have a position
                                if not position_manager.has_position(strategy_id, symbol):
                                    self._execute_buy(strategy_id, symbol, current_price, data)

                            elif signal == 'SELL':
                                # Only sell if we have a position
                                if position_manager.has_position(strategy_id, symbol):
                                    self._execute_sell(strategy_id, symbol, current_price)

                            # Check stop-loss and take-profit for existing positions
                            position = position_manager.get_position(strategy_id, symbol)
                            if position:
                                if position_manager.check_stop_loss(current_price, position):
                                    logger.warning(f"Stop-loss triggered for {symbol} @ ${current_price:.2f}")
                                    self._execute_sell(strategy_id, symbol, current_price, reason="stop_loss")
                                elif position_manager.check_take_profit(current_price, position):
                                    logger.info(f"Take-profit triggered for {symbol} @ ${current_price:.2f}")
                                    self._execute_sell(strategy_id, symbol, current_price, reason="take_profit")

                    # Sleep before next iteration (check every 60 seconds)
                    stop_flag.wait(timeout=60)

                except Exception as e:
                    logger.error(f"Error in strategy {strategy_id} execution loop: {e}")
                    stop_flag.wait(timeout=10)  # Wait before retrying

            logger.info(f"Strategy {strategy_id} execution stopped")

        except Exception as e:
            logger.error(f"Fatal error in strategy {strategy_id}: {e}", exc_info=True)
            if strategy_id in self.running_strategies:
                self.running_strategies[strategy_id]['status'] = 'error'
                self.running_strategies[strategy_id]['error'] = str(e)

    def get_strategy_status(self, strategy_id: str) -> Optional[dict]:
        """Get status of a running strategy"""
        return self.running_strategies.get(strategy_id)

    def is_strategy_running(self, strategy_id: str) -> bool:
        """Check if a strategy is currently running"""
        return strategy_id in self.running_strategies

    def _execute_buy(self, strategy_id: str, symbol: str, current_price: float, data) -> bool:
        """Execute a buy order"""
        try:
            if not self.trading_engine or not self.trading_engine.api:
                logger.warning(f"Cannot execute buy - no trading engine configured (simulation mode)")
                return False

            # Calculate position size (simple: 1% of portfolio per position)
            account = self.trading_engine.api.get_account()
            portfolio_value = float(account.portfolio_value)
            position_value = portfolio_value * 0.01  # 1% per position
            shares = int(position_value / current_price)

            if shares < 1:
                logger.warning(f"Position size too small for {symbol} (${position_value:.2f})")
                return False

            # Calculate stop-loss BEFORE portfolio risk check
            from core.indicators import TechnicalIndicators
            indicators = TechnicalIndicators()
            atr = indicators.calculate_atr(data, period=14)
            stop_loss = current_price - (2 * atr.iloc[-1])

            # Portfolio risk check - verify position won't exceed limits
            existing_positions = [
                {
                    'symbol': p.symbol,
                    'shares': p.shares,
                    'entry_price': p.entry_price,
                    'current_price': p.entry_price,  # Use entry as current for simplicity
                    'stop_loss': p.stop_loss
                }
                for p in position_manager.get_all_positions()
            ]

            can_open, risk_reason = portfolio_risk_manager.can_open_new_position(
                symbol=symbol,
                position_value=position_value,
                stop_loss_price=stop_loss,
                entry_price=current_price,
                existing_positions=existing_positions,
                portfolio_value=portfolio_value
            )

            if not can_open:
                logger.warning(f"❌ {strategy_id}: Position rejected for {symbol} - {risk_reason}")
                notification_system.alert_system_error(
                    error_message=f"Position rejected: {risk_reason}",
                    component=f"Strategy {strategy_id}"
                )
                return False

            logger.info(f"✅ {strategy_id}: Risk check passed - {risk_reason}")

            # Place market buy order
            logger.info(f"🔵 {strategy_id}: Placing BUY order for {shares} {symbol} @ ${current_price:.2f}")

            order = self.trading_engine.place_order(
                symbol=symbol,
                side='buy',
                quantity=shares,
                order_type='market'
            )

            # Track position
            position_manager.add_position(
                strategy_id=strategy_id,
                symbol=symbol,
                shares=shares,
                entry_price=current_price,
                stop_loss=stop_loss
            )

            # Log trade to history
            trade_history.log_trade(
                strategy_id=strategy_id,
                symbol=symbol,
                side='buy',
                shares=shares,
                price=current_price,
                order_type='market',
                status='filled',
                stop_loss=stop_loss,
                alpaca_order_id=order.get('id') if isinstance(order, dict) else None
            )

            # Send notification
            notification_system.alert_trade_executed(
                strategy_id=strategy_id,
                symbol=symbol,
                side='buy',
                shares=shares,
                price=current_price
            )

            logger.info(f"✅ BUY order placed: {shares} {symbol} @ ${current_price:.2f} (Stop: ${stop_loss:.2f})")
            return True

        except Exception as e:
            logger.error(f"Failed to execute buy for {symbol}: {e}")
            return False

    def _execute_sell(self, strategy_id: str, symbol: str, current_price: float, reason: str = "signal") -> bool:
        """Execute a sell order"""
        try:
            if not self.trading_engine or not self.trading_engine.api:
                logger.warning(f"Cannot execute sell - no trading engine configured (simulation mode)")
                return False

            # Get position details
            position = position_manager.get_position(strategy_id, symbol)
            if not position:
                logger.warning(f"Cannot sell {symbol} - no position found")
                return False

            # Place market sell order
            logger.info(f"🔴 {strategy_id}: Placing SELL order for {position.shares} {symbol} @ ${current_price:.2f} (Reason: {reason})")

            order = self.trading_engine.place_order(
                symbol=symbol,
                side='sell',
                quantity=int(position.shares),
                order_type='market'
            )

            # Calculate P&L
            pnl = position.unrealized_pnl(current_price)
            pnl_pct = position.unrealized_pnl_percent(current_price)

            # Calculate hold duration
            from datetime import datetime
            hold_duration_seconds = (datetime.now() - position.entry_time).total_seconds()
            hours = int(hold_duration_seconds // 3600)
            minutes = int((hold_duration_seconds % 3600) // 60)
            hold_duration_str = f"{hours}h {minutes}m"

            # Log trade to history
            trade_history.log_trade(
                strategy_id=strategy_id,
                symbol=symbol,
                side='sell',
                shares=position.shares,
                price=current_price,
                order_type='market',
                status='filled',
                pnl=pnl,
                pnl_percent=pnl_pct,
                entry_price=position.entry_price,
                hold_duration=hold_duration_str,
                notes=reason,
                alpaca_order_id=order.get('id') if isinstance(order, dict) else None
            )

            # Send notification (with appropriate level based on reason)
            if reason == "stop_loss":
                notification_system.alert_stop_loss_triggered(
                    strategy_id=strategy_id,
                    symbol=symbol,
                    entry_price=position.entry_price,
                    stop_price=current_price,
                    pnl=pnl
                )
            else:
                notification_system.alert_trade_executed(
                    strategy_id=strategy_id,
                    symbol=symbol,
                    side='sell',
                    shares=position.shares,
                    price=current_price,
                    pnl=pnl
                )

            # Remove position
            position_manager.remove_position(strategy_id, symbol)

            logger.info(f"✅ SELL order placed: {position.shares} {symbol} @ ${current_price:.2f} | P&L: ${pnl:+.2f} ({pnl_pct:+.2f}%)")
            return True

        except Exception as e:
            logger.error(f"Failed to execute sell for {symbol}: {e}")
            return False


# Global strategy executor instance
strategy_executor = StrategyExecutor()

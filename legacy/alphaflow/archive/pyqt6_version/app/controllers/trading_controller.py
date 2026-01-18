"""Trading controller for managing order execution and position tracking."""

import logging
from typing import Optional, List
from PyQt6.QtCore import QObject, pyqtSignal

from core import (
    OrderManager, Order, OrderType, OrderSide, OrderStatus, TimeInForce,
    TradingMode, PortfolioManager, RiskManager
)


class TradingController(QObject):
    """
    Controller for coordinating trading operations between UI and core modules.

    Responsibilities:
    - Execute orders through OrderManager
    - Track positions via PortfolioManager
    - Enforce risk limits via RiskManager
    - Emit signals for UI updates
    """

    order_placed = pyqtSignal(Order)  # Order placed successfully
    order_filled = pyqtSignal(Order)  # Order filled
    order_canceled = pyqtSignal(Order)  # Order canceled
    order_rejected = pyqtSignal(Order, str)  # Order rejected, reason
    position_updated = pyqtSignal(str, dict)  # symbol, position_data
    error_occurred = pyqtSignal(str)  # error_message

    def __init__(self, trading_mode: TradingMode = TradingMode.PAPER):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.trading_mode = trading_mode

        # Initialize core components
        self.order_manager = OrderManager(trading_mode)
        self.portfolio_manager = PortfolioManager(initial_capital=100000)
        self.risk_manager = RiskManager(initial_capital=100000)

        self.logger.info(f"TradingController initialized in {trading_mode.value} mode")

    def set_trading_mode(self, mode: TradingMode):
        """
        Change trading mode.

        Args:
            mode: New trading mode
        """
        if mode == self.trading_mode:
            return

        self.logger.warning(f"Changing trading mode from {self.trading_mode.value} to {mode.value}")
        self.trading_mode = mode
        self.order_manager = OrderManager(mode)

    def place_market_order(
        self,
        symbol: str,
        side: OrderSide,
        quantity: float
    ) -> Optional[Order]:
        """
        Place a market order.

        Args:
            symbol: Stock symbol
            side: BUY or SELL
            quantity: Number of shares

        Returns:
            Order object if successful, None otherwise
        """
        # Risk checks
        if not self._validate_order(symbol, side, quantity):
            return None

        # Create order
        order = self.order_manager.create_order(
            symbol=symbol,
            side=side,
            quantity=quantity,
            order_type=OrderType.MARKET
        )

        if not order:
            error_msg = "Failed to create order"
            self.logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            return None

        # Submit order
        success = self.order_manager.submit_order(order)

        if success:
            self.logger.info(f"Market order placed: {side.value} {quantity} {symbol}")
            self.order_placed.emit(order)

            # Update portfolio if filled (in backtest/paper mode, orders fill immediately)
            if order.status == OrderStatus.FILLED:
                self._handle_order_fill(order)

            return order
        else:
            self.logger.error(f"Order submission failed: {order.error_message}")
            self.order_rejected.emit(order, order.error_message or "Unknown error")
            return None

    def place_limit_order(
        self,
        symbol: str,
        side: OrderSide,
        quantity: float,
        limit_price: float
    ) -> Optional[Order]:
        """
        Place a limit order.

        Args:
            symbol: Stock symbol
            side: BUY or SELL
            quantity: Number of shares
            limit_price: Limit price

        Returns:
            Order object if successful, None otherwise
        """
        # Risk checks
        if not self._validate_order(symbol, side, quantity, limit_price):
            return None

        # Create order
        order = self.order_manager.create_order(
            symbol=symbol,
            side=side,
            quantity=quantity,
            order_type=OrderType.LIMIT,
            limit_price=limit_price
        )

        if not order:
            error_msg = "Failed to create order"
            self.logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            return None

        # Submit order
        success = self.order_manager.submit_order(order)

        if success:
            self.logger.info(f"Limit order placed: {side.value} {quantity} {symbol} @ ${limit_price}")
            self.order_placed.emit(order)
            return order
        else:
            self.logger.error(f"Order submission failed: {order.error_message}")
            self.order_rejected.emit(order, order.error_message or "Unknown error")
            return None

    def cancel_order(self, client_order_id: str) -> bool:
        """
        Cancel an order.

        Args:
            client_order_id: Client order ID

        Returns:
            True if canceled successfully
        """
        success = self.order_manager.cancel_order(client_order_id)

        if success:
            order = self.order_manager.get_order(client_order_id)
            if order:
                self.logger.info(f"Order canceled: {client_order_id}")
                self.order_canceled.emit(order)
            return True
        else:
            error_msg = f"Failed to cancel order: {client_order_id}"
            self.logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            return False

    def get_positions(self) -> List[dict]:
        """
        Get all current positions.

        Returns:
            List of position dictionaries
        """
        positions = []
        for symbol, position in self.portfolio_manager.positions.items():
            positions.append({
                'symbol': symbol,
                'quantity': position.quantity,
                'avg_price': position.average_price,
                'current_price': position.current_price,
                'unrealized_pnl': position.unrealized_pnl,
                'unrealized_pnl_percent': position.unrealized_pnl_percent,
            })
        return positions

    def get_orders(self, status: Optional[OrderStatus] = None) -> List[Order]:
        """
        Get orders, optionally filtered by status.

        Args:
            status: Optional status filter

        Returns:
            List of orders
        """
        all_orders = self.order_manager.get_all_orders()

        if status:
            return [o for o in all_orders if o.status == status]

        return all_orders

    def get_portfolio_value(self) -> float:
        """Get current portfolio value."""
        return self.portfolio_manager.get_portfolio_value()

    def get_cash_balance(self) -> float:
        """Get current cash balance."""
        return self.portfolio_manager.cash

    def update_positions(self, prices: dict):
        """
        Update position prices.

        Args:
            prices: Dictionary mapping symbols to current prices
        """
        for symbol, price in prices.items():
            self.portfolio_manager.update_position_price(symbol, price)
            self.position_updated.emit(symbol, {'current_price': price})

    def _validate_order(
        self,
        symbol: str,
        side: OrderSide,
        quantity: float,
        price: Optional[float] = None
    ) -> bool:
        """
        Validate order against risk limits.

        Args:
            symbol: Stock symbol
            side: BUY or SELL
            quantity: Number of shares
            price: Price (for position size calculation)

        Returns:
            True if order passes validation
        """
        # Basic validation
        if quantity <= 0:
            error_msg = "Quantity must be positive"
            self.logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            return False

        # Position size check for BUY orders
        if side == OrderSide.BUY:
            if price:
                position_value = quantity * price
                portfolio_value = self.get_portfolio_value()

                if portfolio_value > 0:
                    position_size = position_value / portfolio_value

                    # Check against risk limits
                    if not self.risk_manager.validate_position_size(position_size):
                        error_msg = f"Position size {position_size:.1%} exceeds maximum allowed"
                        self.logger.error(error_msg)
                        self.error_occurred.emit(error_msg)
                        return False

        # Check cash balance for BUY orders
        if side == OrderSide.BUY and price:
            order_value = quantity * price
            if order_value > self.get_cash_balance():
                error_msg = "Insufficient cash balance"
                self.logger.error(error_msg)
                self.error_occurred.emit(error_msg)
                return False

        # Check if we have position for SELL orders
        if side == OrderSide.SELL:
            position = self.portfolio_manager.positions.get(symbol)
            if not position or position.quantity < quantity:
                error_msg = f"Insufficient position to sell {quantity} shares of {symbol}"
                self.logger.error(error_msg)
                self.error_occurred.emit(error_msg)
                return False

        return True

    def _handle_order_fill(self, order: Order):
        """
        Handle order fill - update portfolio.

        Args:
            order: Filled order
        """
        # Update portfolio
        if order.side == OrderSide.BUY:
            self.portfolio_manager.add_position(
                symbol=order.symbol,
                quantity=order.filled_quantity,
                price=order.filled_avg_price or 0.0
            )
        else:  # SELL
            self.portfolio_manager.close_position(
                symbol=order.symbol,
                quantity=order.filled_quantity,
                price=order.filled_avg_price or 0.0
            )

        self.logger.info(f"Portfolio updated after fill: {order.symbol}")
        self.order_filled.emit(order)

        # Update risk manager
        self.risk_manager.update_from_portfolio(self.portfolio_manager)

    def cleanup(self):
        """Clean up resources."""
        self.logger.info("TradingController cleanup")

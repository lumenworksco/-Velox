"""Order management system for AlphaFlow Trading Platform."""

import logging
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum
from dataclasses import dataclass, field

from .config import ALPACA_AVAILABLE, TradingMode

if ALPACA_AVAILABLE:
    from alpaca_trade_api import REST
    from alpaca_trade_api.rest import APIError


class OrderType(Enum):
    """Order type enumeration."""
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"
    TRAILING_STOP = "trailing_stop"


class OrderSide(Enum):
    """Order side enumeration."""
    BUY = "buy"
    SELL = "sell"


class OrderStatus(Enum):
    """Order status enumeration."""
    PENDING = "pending"
    SUBMITTED = "submitted"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELED = "canceled"
    REJECTED = "rejected"
    EXPIRED = "expired"


class TimeInForce(Enum):
    """Time in force enumeration."""
    DAY = "day"          # Day order
    GTC = "gtc"          # Good till canceled
    IOC = "ioc"          # Immediate or cancel
    FOK = "fok"          # Fill or kill


@dataclass
class Order:
    """Represents a trading order."""
    symbol: str
    side: OrderSide
    quantity: float
    order_type: OrderType
    status: OrderStatus = OrderStatus.PENDING
    limit_price: Optional[float] = None
    stop_price: Optional[float] = None
    time_in_force: TimeInForce = TimeInForce.DAY
    order_id: Optional[str] = None
    client_order_id: Optional[str] = None
    filled_quantity: float = 0.0
    filled_avg_price: Optional[float] = None
    submitted_at: Optional[datetime] = None
    filled_at: Optional[datetime] = None
    canceled_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    error_message: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert order to dictionary."""
        return {
            'symbol': self.symbol,
            'side': self.side.value,
            'quantity': self.quantity,
            'order_type': self.order_type.value,
            'status': self.status.value,
            'limit_price': self.limit_price,
            'stop_price': self.stop_price,
            'time_in_force': self.time_in_force.value,
            'order_id': self.order_id,
            'client_order_id': self.client_order_id,
            'filled_quantity': self.filled_quantity,
            'filled_avg_price': self.filled_avg_price,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'filled_at': self.filled_at.isoformat() if self.filled_at else None,
            'canceled_at': self.canceled_at.isoformat() if self.canceled_at else None,
            'created_at': self.created_at.isoformat(),
            'error_message': self.error_message,
        }


class OrderManager:
    """Manages order execution and tracking."""

    def __init__(self, trading_mode: TradingMode = TradingMode.PAPER):
        """
        Initialize the order manager.

        Args:
            trading_mode: Trading mode (LIVE, PAPER, BACKTEST, ANALYSIS)
        """
        self.logger = logging.getLogger(__name__)
        self.trading_mode = trading_mode
        self.orders: Dict[str, Order] = {}
        self.alpaca_api: Optional[REST] = None

        # Initialize Alpaca API if in live or paper mode
        if trading_mode in [TradingMode.LIVE, TradingMode.PAPER]:
            self._initialize_alpaca()

    def _initialize_alpaca(self):
        """Initialize Alpaca API connection."""
        if not ALPACA_AVAILABLE:
            self.logger.error("Alpaca API not available. Install alpaca-trade-api.")
            return

        try:
            import os
            api_key = os.getenv('ALPACA_API_KEY')
            api_secret = os.getenv('ALPACA_SECRET_KEY')

            if not api_key or not api_secret:
                self.logger.error("Alpaca API credentials not found in environment variables.")
                return

            # Use paper trading endpoint for PAPER mode
            base_url = 'https://paper-api.alpaca.markets' if self.trading_mode == TradingMode.PAPER else 'https://api.alpaca.markets'

            self.alpaca_api = REST(
                key_id=api_key,
                secret_key=api_secret,
                base_url=base_url
            )

            # Test connection
            account = self.alpaca_api.get_account()
            self.logger.info(f"Alpaca API connected. Account: {account.account_number} ({self.trading_mode.value} mode)")

        except Exception as e:
            self.logger.error(f"Failed to initialize Alpaca API: {e}")
            self.alpaca_api = None

    def create_order(
        self,
        symbol: str,
        side: OrderSide,
        quantity: float,
        order_type: OrderType = OrderType.MARKET,
        limit_price: Optional[float] = None,
        stop_price: Optional[float] = None,
        time_in_force: TimeInForce = TimeInForce.DAY
    ) -> Optional[Order]:
        """
        Create a new order.

        Args:
            symbol: Stock symbol
            side: Buy or sell
            quantity: Number of shares
            order_type: Order type (market, limit, etc.)
            limit_price: Limit price (required for limit orders)
            stop_price: Stop price (required for stop orders)
            time_in_force: Time in force

        Returns:
            Order object if created successfully, None otherwise
        """
        # Validation
        if order_type == OrderType.LIMIT and limit_price is None:
            self.logger.error("Limit price required for limit orders")
            return None

        if order_type in [OrderType.STOP, OrderType.STOP_LIMIT] and stop_price is None:
            self.logger.error("Stop price required for stop orders")
            return None

        # Create order object
        order = Order(
            symbol=symbol,
            side=side,
            quantity=quantity,
            order_type=order_type,
            limit_price=limit_price,
            stop_price=stop_price,
            time_in_force=time_in_force
        )

        # Generate client order ID
        order.client_order_id = f"alphaflow_{int(datetime.now().timestamp() * 1000)}"

        # Store order
        self.orders[order.client_order_id] = order

        self.logger.info(f"Created order: {side.value} {quantity} {symbol} ({order_type.value})")

        return order

    def submit_order(self, order: Order) -> bool:
        """
        Submit an order for execution.

        Args:
            order: Order to submit

        Returns:
            True if submitted successfully, False otherwise
        """
        if self.trading_mode == TradingMode.ANALYSIS:
            self.logger.warning("Cannot submit orders in ANALYSIS mode")
            return False

        if self.trading_mode == TradingMode.BACKTEST:
            # In backtest mode, simulate immediate fill at current price
            return self._simulate_backtest_fill(order)

        # Submit to Alpaca (LIVE or PAPER mode)
        if self.alpaca_api is None:
            self.logger.error("Alpaca API not initialized")
            order.status = OrderStatus.REJECTED
            order.error_message = "API not initialized"
            return False

        try:
            # Prepare order parameters
            alpaca_order = self.alpaca_api.submit_order(
                symbol=order.symbol,
                qty=order.quantity,
                side=order.side.value,
                type=order.order_type.value,
                time_in_force=order.time_in_force.value,
                limit_price=str(order.limit_price) if order.limit_price else None,
                stop_price=str(order.stop_price) if order.stop_price else None,
                client_order_id=order.client_order_id
            )

            # Update order with Alpaca response
            order.order_id = alpaca_order.id
            order.status = OrderStatus.SUBMITTED
            order.submitted_at = datetime.now()

            self.logger.info(f"Order submitted: {order.order_id}")
            return True

        except APIError as e:
            self.logger.error(f"Alpaca API error submitting order: {e}")
            order.status = OrderStatus.REJECTED
            order.error_message = str(e)
            return False
        except Exception as e:
            self.logger.error(f"Error submitting order: {e}")
            order.status = OrderStatus.REJECTED
            order.error_message = str(e)
            return False

    def _simulate_backtest_fill(self, order: Order) -> bool:
        """Simulate order fill for backtesting."""
        order.status = OrderStatus.FILLED
        order.filled_quantity = order.quantity
        order.submitted_at = datetime.now()
        order.filled_at = datetime.now()

        # Use limit price if available, otherwise simulate market price
        order.filled_avg_price = order.limit_price if order.limit_price else 100.0

        self.logger.info(f"Simulated fill: {order.symbol} {order.quantity} @ {order.filled_avg_price}")
        return True

    def cancel_order(self, client_order_id: str) -> bool:
        """
        Cancel an order.

        Args:
            client_order_id: Client order ID

        Returns:
            True if canceled successfully, False otherwise
        """
        order = self.orders.get(client_order_id)
        if not order:
            self.logger.error(f"Order not found: {client_order_id}")
            return False

        if order.status in [OrderStatus.FILLED, OrderStatus.CANCELED, OrderStatus.REJECTED]:
            self.logger.warning(f"Cannot cancel order in {order.status.value} status")
            return False

        if self.trading_mode == TradingMode.BACKTEST:
            order.status = OrderStatus.CANCELED
            order.canceled_at = datetime.now()
            return True

        if self.alpaca_api and order.order_id:
            try:
                self.alpaca_api.cancel_order(order.order_id)
                order.status = OrderStatus.CANCELED
                order.canceled_at = datetime.now()
                self.logger.info(f"Order canceled: {order.order_id}")
                return True
            except Exception as e:
                self.logger.error(f"Error canceling order: {e}")
                return False

        return False

    def update_order_status(self, client_order_id: str):
        """
        Update order status from Alpaca API.

        Args:
            client_order_id: Client order ID
        """
        order = self.orders.get(client_order_id)
        if not order or not order.order_id:
            return

        if self.alpaca_api is None:
            return

        try:
            alpaca_order = self.alpaca_api.get_order(order.order_id)

            # Update status
            status_mapping = {
                'new': OrderStatus.SUBMITTED,
                'partially_filled': OrderStatus.PARTIALLY_FILLED,
                'filled': OrderStatus.FILLED,
                'canceled': OrderStatus.CANCELED,
                'rejected': OrderStatus.REJECTED,
                'expired': OrderStatus.EXPIRED,
            }

            order.status = status_mapping.get(alpaca_order.status, OrderStatus.PENDING)
            order.filled_quantity = float(alpaca_order.filled_qty or 0)

            if alpaca_order.filled_avg_price:
                order.filled_avg_price = float(alpaca_order.filled_avg_price)

            if alpaca_order.filled_at:
                order.filled_at = alpaca_order.filled_at

        except Exception as e:
            self.logger.error(f"Error updating order status: {e}")

    def get_order(self, client_order_id: str) -> Optional[Order]:
        """Get order by client order ID."""
        return self.orders.get(client_order_id)

    def get_all_orders(self) -> List[Order]:
        """Get all orders."""
        return list(self.orders.values())

    def get_open_orders(self) -> List[Order]:
        """Get all open orders (submitted or partially filled)."""
        return [
            order for order in self.orders.values()
            if order.status in [OrderStatus.SUBMITTED, OrderStatus.PARTIALLY_FILLED]
        ]

    def get_filled_orders(self) -> List[Order]:
        """Get all filled orders."""
        return [
            order for order in self.orders.values()
            if order.status == OrderStatus.FILLED
        ]

    def clear_old_orders(self, days: int = 7):
        """Clear orders older than specified days."""
        cutoff = datetime.now().timestamp() - (days * 24 * 60 * 60)

        self.orders = {
            oid: order for oid, order in self.orders.items()
            if order.created_at.timestamp() > cutoff or order.status in [OrderStatus.SUBMITTED, OrderStatus.PARTIALLY_FILLED]
        }

        self.logger.info(f"Cleared orders older than {days} days")

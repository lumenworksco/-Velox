"""Alert and notification system for price and signal alerts."""

import logging
from typing import Dict, List, Optional, Callable
from datetime import datetime
from enum import Enum
from dataclasses import dataclass

from PyQt6.QtCore import QObject, pyqtSignal, QTimer


class AlertType(Enum):
    """Alert type enumeration."""
    PRICE_ABOVE = "price_above"
    PRICE_BELOW = "price_below"
    PERCENT_CHANGE = "percent_change"
    RSI_OVERBOUGHT = "rsi_overbought"
    RSI_OVERSOLD = "rsi_oversold"
    MACD_BULLISH = "macd_bullish"
    MACD_BEARISH = "macd_bearish"
    VOLUME_SPIKE = "volume_spike"
    MA_CROSSOVER = "ma_crossover"
    CUSTOM = "custom"


class AlertStatus(Enum):
    """Alert status enumeration."""
    ACTIVE = "active"
    TRIGGERED = "triggered"
    DISABLED = "disabled"


@dataclass
class Alert:
    """Alert configuration."""
    id: str
    symbol: str
    alert_type: AlertType
    condition_value: float
    status: AlertStatus = AlertStatus.ACTIVE
    created_at: datetime = None
    triggered_at: Optional[datetime] = None
    message: str = ""
    repeating: bool = False

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


class AlertManager(QObject):
    """
    Manages price and signal alerts.

    Features:
    - Price alerts (above/below threshold)
    - Percentage change alerts
    - Technical indicator alerts (RSI, MACD, etc.)
    - Volume spike alerts
    - Custom alerts
    """

    alert_triggered = pyqtSignal(Alert)  # Alert that was triggered
    alert_created = pyqtSignal(Alert)  # New alert created
    alert_deleted = pyqtSignal(str)  # Alert ID deleted

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)

        # Active alerts
        self.alerts: Dict[str, Alert] = {}

        # Alert check timer
        self.check_timer = QTimer()
        self.check_timer.timeout.connect(self._check_alerts)
        self.check_timer.start(5000)  # Check every 5 seconds

        # Latest market data cache (will be updated by DataController)
        self.market_data_cache: Dict[str, dict] = {}

    def create_alert(
        self,
        symbol: str,
        alert_type: AlertType,
        condition_value: float,
        message: str = "",
        repeating: bool = False
    ) -> Alert:
        """
        Create a new alert.

        Args:
            symbol: Stock symbol
            alert_type: Type of alert
            condition_value: Threshold value for the alert
            message: Custom message (optional)
            repeating: Whether alert repeats after triggering

        Returns:
            Created Alert object
        """
        alert_id = f"{symbol}_{alert_type.value}_{datetime.now().timestamp()}"

        alert = Alert(
            id=alert_id,
            symbol=symbol,
            alert_type=alert_type,
            condition_value=condition_value,
            message=message,
            repeating=repeating
        )

        self.alerts[alert_id] = alert
        self.alert_created.emit(alert)

        self.logger.info(f"Alert created: {symbol} {alert_type.value} @ {condition_value}")

        return alert

    def delete_alert(self, alert_id: str):
        """
        Delete an alert.

        Args:
            alert_id: Alert ID to delete
        """
        if alert_id in self.alerts:
            del self.alerts[alert_id]
            self.alert_deleted.emit(alert_id)
            self.logger.info(f"Alert deleted: {alert_id}")

    def update_market_data(self, symbol: str, data: dict):
        """
        Update market data cache for alert checking.

        Args:
            symbol: Stock symbol
            data: Market data dictionary
        """
        self.market_data_cache[symbol] = data

    def _check_alerts(self):
        """Check all active alerts against current market data."""
        for alert_id, alert in list(self.alerts.items()):
            if alert.status != AlertStatus.ACTIVE:
                continue

            # Check if we have data for this symbol
            if alert.symbol not in self.market_data_cache:
                continue

            data = self.market_data_cache[alert.symbol]

            # Check alert condition
            if self._check_alert_condition(alert, data):
                self._trigger_alert(alert)

    def _check_alert_condition(self, alert: Alert, data: dict) -> bool:
        """
        Check if alert condition is met.

        Args:
            alert: Alert to check
            data: Market data

        Returns:
            True if condition is met
        """
        quote = data.get('quote', {})
        df = data.get('historical')

        if alert.alert_type == AlertType.PRICE_ABOVE:
            current_price = quote.get('price', 0)
            return current_price >= alert.condition_value

        elif alert.alert_type == AlertType.PRICE_BELOW:
            current_price = quote.get('price', 0)
            return current_price <= alert.condition_value

        elif alert.alert_type == AlertType.PERCENT_CHANGE:
            change_pct = quote.get('change_percent', 0)
            return abs(change_pct) >= alert.condition_value

        elif alert.alert_type == AlertType.RSI_OVERBOUGHT:
            if df is not None and 'rsi' in df.columns:
                latest_rsi = df.iloc[-1]['rsi']
                return latest_rsi >= alert.condition_value

        elif alert.alert_type == AlertType.RSI_OVERSOLD:
            if df is not None and 'rsi' in df.columns:
                latest_rsi = df.iloc[-1]['rsi']
                return latest_rsi <= alert.condition_value

        elif alert.alert_type == AlertType.MACD_BULLISH:
            if df is not None and 'macd' in df.columns and 'macd_signal' in df.columns:
                macd = df.iloc[-1]['macd']
                signal = df.iloc[-1]['macd_signal']
                prev_macd = df.iloc[-2]['macd']
                prev_signal = df.iloc[-2]['macd_signal']
                # Bullish crossover: MACD crosses above signal
                return prev_macd <= prev_signal and macd > signal

        elif alert.alert_type == AlertType.MACD_BEARISH:
            if df is not None and 'macd' in df.columns and 'macd_signal' in df.columns:
                macd = df.iloc[-1]['macd']
                signal = df.iloc[-1]['macd_signal']
                prev_macd = df.iloc[-2]['macd']
                prev_signal = df.iloc[-2]['macd_signal']
                # Bearish crossover: MACD crosses below signal
                return prev_macd >= prev_signal and macd < signal

        elif alert.alert_type == AlertType.VOLUME_SPIKE:
            if df is not None and 'volume' in df.columns:
                latest_volume = df.iloc[-1]['volume']
                avg_volume = df['volume'].rolling(20).mean().iloc[-1]
                return latest_volume >= avg_volume * alert.condition_value

        elif alert.alert_type == AlertType.MA_CROSSOVER:
            if df is not None and 'sma_20' in df.columns and 'sma_50' in df.columns:
                sma_20 = df.iloc[-1]['sma_20']
                sma_50 = df.iloc[-1]['sma_50']
                prev_sma_20 = df.iloc[-2]['sma_20']
                prev_sma_50 = df.iloc[-2]['sma_50']
                # Bullish crossover: SMA 20 crosses above SMA 50
                return prev_sma_20 <= prev_sma_50 and sma_20 > sma_50

        return False

    def _trigger_alert(self, alert: Alert):
        """
        Trigger an alert.

        Args:
            alert: Alert to trigger
        """
        alert.triggered_at = datetime.now()

        # Update status (unless repeating)
        if not alert.repeating:
            alert.status = AlertStatus.TRIGGERED

        # Emit signal
        self.alert_triggered.emit(alert)

        self.logger.info(f"Alert triggered: {alert.symbol} {alert.alert_type.value}")

    def get_active_alerts(self) -> List[Alert]:
        """Get all active alerts."""
        return [a for a in self.alerts.values() if a.status == AlertStatus.ACTIVE]

    def get_triggered_alerts(self) -> List[Alert]:
        """Get all triggered alerts."""
        return [a for a in self.alerts.values() if a.status == AlertStatus.TRIGGERED]

    def get_alerts_for_symbol(self, symbol: str) -> List[Alert]:
        """Get all alerts for a specific symbol."""
        return [a for a in self.alerts.values() if a.symbol == symbol]

    def disable_alert(self, alert_id: str):
        """Disable an alert without deleting it."""
        if alert_id in self.alerts:
            self.alerts[alert_id].status = AlertStatus.DISABLED

    def enable_alert(self, alert_id: str):
        """Re-enable a disabled alert."""
        if alert_id in self.alerts:
            self.alerts[alert_id].status = AlertStatus.ACTIVE

    def clear_triggered_alerts(self):
        """Clear all triggered alerts."""
        triggered = [aid for aid, a in self.alerts.items() if a.status == AlertStatus.TRIGGERED]
        for alert_id in triggered:
            del self.alerts[alert_id]

    def get_alert_summary(self) -> dict:
        """Get summary of alerts."""
        return {
            'total': len(self.alerts),
            'active': len([a for a in self.alerts.values() if a.status == AlertStatus.ACTIVE]),
            'triggered': len([a for a in self.alerts.values() if a.status == AlertStatus.TRIGGERED]),
            'disabled': len([a for a in self.alerts.values() if a.status == AlertStatus.DISABLED]),
        }

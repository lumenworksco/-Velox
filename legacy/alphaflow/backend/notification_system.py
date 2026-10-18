"""Notification and alert system for trading events"""

import logging
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, List
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class AlertLevel(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertType(Enum):
    """Types of alerts"""
    TRADE_EXECUTED = "trade_executed"
    STOP_LOSS_TRIGGERED = "stop_loss_triggered"
    TAKE_PROFIT_TRIGGERED = "take_profit_triggered"
    DAILY_LOSS_LIMIT = "daily_loss_limit"
    STRATEGY_STARTED = "strategy_started"
    STRATEGY_STOPPED = "strategy_stopped"
    EMERGENCY_STOP = "emergency_stop"
    SYSTEM_ERROR = "system_error"
    TRADING_MODE_CHANGED = "trading_mode_changed"


class NotificationSystem:
    """Manages notifications and alerts"""

    def __init__(self):
        """Initialize notification system"""
        self.email_enabled = False
        self.slack_enabled = False
        self.console_enabled = True  # Always log to console

        # Email configuration from environment
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_username = os.getenv('SMTP_USERNAME')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        self.email_from = os.getenv('EMAIL_FROM', self.smtp_username)
        self.email_to = os.getenv('EMAIL_TO', '').split(',') if os.getenv('EMAIL_TO') else []

        # Slack configuration from environment
        self.slack_webhook_url = os.getenv('SLACK_WEBHOOK_URL')

        # Enable channels based on configuration
        if self.smtp_username and self.smtp_password and self.email_to:
            self.email_enabled = True
            logger.info("✅ Email notifications enabled")
        else:
            logger.info("ℹ️ Email notifications disabled (no configuration)")

        if self.slack_webhook_url:
            self.slack_enabled = True
            logger.info("✅ Slack notifications enabled")
        else:
            logger.info("ℹ️ Slack notifications disabled (no webhook URL)")

    def send_alert(
        self,
        alert_type: AlertType,
        level: AlertLevel,
        title: str,
        message: str,
        details: Optional[dict] = None
    ):
        """
        Send an alert via all configured channels

        Args:
            alert_type: Type of alert
            level: Severity level
            title: Alert title
            message: Alert message
            details: Optional additional details
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Format full message
        full_message = f"""
🕐 {timestamp}
📋 {title}

{message}
"""

        if details:
            full_message += "\n📊 Details:\n"
            for key, value in details.items():
                full_message += f"  • {key}: {value}\n"

        # Console logging (always enabled)
        if self.console_enabled:
            self._log_to_console(level, title, message, details)

        # Email notifications
        if self.email_enabled:
            try:
                self._send_email(level, title, full_message)
            except Exception as e:
                logger.error(f"Failed to send email notification: {e}")

        # Slack notifications
        if self.slack_enabled:
            try:
                self._send_slack(level, title, message, details)
            except Exception as e:
                logger.error(f"Failed to send Slack notification: {e}")

    def _log_to_console(
        self,
        level: AlertLevel,
        title: str,
        message: str,
        details: Optional[dict]
    ):
        """Log alert to console"""
        emoji = {
            AlertLevel.INFO: "ℹ️",
            AlertLevel.WARNING: "⚠️",
            AlertLevel.CRITICAL: "🚨"
        }

        log_message = f"{emoji[level]} {title}: {message}"
        if details:
            log_message += f" | Details: {details}"

        if level == AlertLevel.CRITICAL:
            logger.critical(log_message)
        elif level == AlertLevel.WARNING:
            logger.warning(log_message)
        else:
            logger.info(log_message)

    def _send_email(self, level: AlertLevel, title: str, message: str):
        """Send email notification"""
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email_from
            msg['To'] = ', '.join(self.email_to)
            msg['Subject'] = f"[AlphaFlow {level.value.upper()}] {title}"

            # Email body
            body = f"""
<html>
<head>
<style>
body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
.header {{ background-color: {'#f44336' if level == AlertLevel.CRITICAL else '#ff9800' if level == AlertLevel.WARNING else '#2196F3'}; color: white; padding: 20px; }}
.content {{ padding: 20px; }}
.footer {{ background-color: #f5f5f5; padding: 10px; text-align: center; font-size: 12px; }}
</style>
</head>
<body>
<div class="header">
<h2>{title}</h2>
</div>
<div class="content">
<pre>{message}</pre>
</div>
<div class="footer">
AlphaFlow Algorithmic Trading Platform
</div>
</body>
</html>
"""
            msg.attach(MIMEText(body, 'html'))

            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)

            logger.debug(f"Email notification sent: {title}")
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            raise

    def _send_slack(
        self,
        level: AlertLevel,
        title: str,
        message: str,
        details: Optional[dict]
    ):
        """Send Slack notification"""
        try:
            import requests

            # Color based on level
            color = {
                AlertLevel.CRITICAL: "#f44336",
                AlertLevel.WARNING: "#ff9800",
                AlertLevel.INFO: "#2196F3"
            }

            # Format details
            fields = []
            if details:
                for key, value in details.items():
                    fields.append({
                        "title": key,
                        "value": str(value),
                        "short": True
                    })

            # Slack message payload
            payload = {
                "attachments": [
                    {
                        "color": color[level],
                        "title": title,
                        "text": message,
                        "fields": fields,
                        "footer": "AlphaFlow Trading Platform",
                        "ts": int(datetime.now().timestamp())
                    }
                ]
            }

            response = requests.post(self.slack_webhook_url, json=payload)
            response.raise_for_status()

            logger.debug(f"Slack notification sent: {title}")
        except Exception as e:
            logger.error(f"Failed to send Slack notification: {e}")
            raise

    # Convenience methods for common alerts

    def alert_trade_executed(
        self,
        strategy_id: str,
        symbol: str,
        side: str,
        shares: float,
        price: float,
        pnl: Optional[float] = None
    ):
        """Alert when a trade is executed"""
        pnl_str = f" | P&L: ${pnl:+.2f}" if pnl is not None else ""
        self.send_alert(
            alert_type=AlertType.TRADE_EXECUTED,
            level=AlertLevel.INFO,
            title=f"Trade Executed: {side.upper()} {symbol}",
            message=f"Strategy '{strategy_id}' executed {side.upper()} order for {shares} shares of {symbol} @ ${price:.2f}{pnl_str}",
            details={
                "Strategy": strategy_id,
                "Symbol": symbol,
                "Side": side.upper(),
                "Shares": shares,
                "Price": f"${price:.2f}",
                "P&L": f"${pnl:+.2f}" if pnl else "N/A"
            }
        )

    def alert_stop_loss_triggered(
        self,
        strategy_id: str,
        symbol: str,
        entry_price: float,
        stop_price: float,
        pnl: float
    ):
        """Alert when stop-loss is triggered"""
        self.send_alert(
            alert_type=AlertType.STOP_LOSS_TRIGGERED,
            level=AlertLevel.WARNING,
            title=f"Stop-Loss Triggered: {symbol}",
            message=f"Stop-loss triggered for {symbol} in strategy '{strategy_id}'",
            details={
                "Strategy": strategy_id,
                "Symbol": symbol,
                "Entry Price": f"${entry_price:.2f}",
                "Stop Price": f"${stop_price:.2f}",
                "Loss": f"${pnl:.2f}"
            }
        )

    def alert_daily_loss_limit(self, daily_pnl: float, limit_percent: float):
        """Alert when daily loss limit is reached"""
        self.send_alert(
            alert_type=AlertType.DAILY_LOSS_LIMIT,
            level=AlertLevel.CRITICAL,
            title="Daily Loss Limit Reached",
            message=f"Daily loss of {daily_pnl:.2f}% has reached the limit of {limit_percent}%. All trading has been halted.",
            details={
                "Daily P&L": f"{daily_pnl:.2f}%",
                "Limit": f"{limit_percent}%",
                "Action": "All strategies stopped"
            }
        )

    def alert_emergency_stop(self, stopped_strategies: List[str], closed_positions: List[str]):
        """Alert when emergency stop is triggered"""
        self.send_alert(
            alert_type=AlertType.EMERGENCY_STOP,
            level=AlertLevel.CRITICAL,
            title="EMERGENCY STOP EXECUTED",
            message=f"Emergency stop activated. {len(stopped_strategies)} strategies stopped, {len(closed_positions)} positions closed.",
            details={
                "Strategies Stopped": len(stopped_strategies),
                "Positions Closed": len(closed_positions),
                "Stopped Strategies": ", ".join(stopped_strategies),
                "Closed Positions": ", ".join(closed_positions)
            }
        )

    def alert_trading_mode_changed(self, old_mode: str, new_mode: str):
        """Alert when trading mode changes"""
        level = AlertLevel.CRITICAL if new_mode == "live" else AlertLevel.WARNING
        self.send_alert(
            alert_type=AlertType.TRADING_MODE_CHANGED,
            level=level,
            title="Trading Mode Changed",
            message=f"Trading mode changed from {old_mode.upper()} to {new_mode.upper()}",
            details={
                "Previous Mode": old_mode.upper(),
                "New Mode": new_mode.upper(),
                "Warning": "REAL MONEY AT RISK" if new_mode == "live" else "Simulated trading"
            }
        )

    def alert_strategy_started(self, strategy_id: str, symbols: List[str]):
        """Alert when strategy starts"""
        self.send_alert(
            alert_type=AlertType.STRATEGY_STARTED,
            level=AlertLevel.INFO,
            title=f"Strategy Started: {strategy_id}",
            message=f"Strategy '{strategy_id}' has been started and is now trading",
            details={
                "Strategy": strategy_id,
                "Symbols": ", ".join(symbols),
                "Status": "Active"
            }
        )

    def alert_strategy_stopped(self, strategy_id: str, reason: str = "User request"):
        """Alert when strategy stops"""
        self.send_alert(
            alert_type=AlertType.STRATEGY_STOPPED,
            level=AlertLevel.WARNING,
            title=f"Strategy Stopped: {strategy_id}",
            message=f"Strategy '{strategy_id}' has been stopped",
            details={
                "Strategy": strategy_id,
                "Reason": reason,
                "Status": "Stopped"
            }
        )

    def alert_system_error(self, error_message: str, component: str):
        """Alert for system errors"""
        self.send_alert(
            alert_type=AlertType.SYSTEM_ERROR,
            level=AlertLevel.CRITICAL,
            title="System Error",
            message=f"Error in {component}: {error_message}",
            details={
                "Component": component,
                "Error": error_message,
                "Action": "Review logs and take corrective action"
            }
        )


# Global notification system instance
notification_system = NotificationSystem()

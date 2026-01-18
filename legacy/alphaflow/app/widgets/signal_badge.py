"""Signal badge widget for displaying BUY/SELL/HOLD signals."""

from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from app.styles import COLORS, SIGNAL_COLORS


class SignalBadge(QLabel):
    """
    A badge widget for displaying trading signals (BUY/SELL/HOLD).

    Features:
    - Color-coded background
    - Icon + text
    - Compact design
    """

    def __init__(self, signal: str = "HOLD", confidence: float = 0.0, parent=None):
        super().__init__(parent)
        self.signal = signal.upper()
        self.confidence = confidence

        self._setup_ui()
        self._update_display()

    def _setup_ui(self):
        """Setup the badge UI."""
        font = QFont()
        font.setFamilies(['Inter', 'SF Pro Display', 'Segoe UI'])
        font.setPointSize(11)
        font.setWeight(QFont.Weight.Bold)
        self.setFont(font)

        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFixedHeight(32)
        self.setMinimumWidth(80)

    def _update_display(self):
        """Update the badge display based on signal."""
        # Get signal icon and color
        signal_config = {
            'BUY': {'icon': '↑', 'color': SIGNAL_COLORS['BUY'], 'text': 'BUY'},
            'SELL': {'icon': '↓', 'color': SIGNAL_COLORS['SELL'], 'text': 'SELL'},
            'HOLD': {'icon': '⊙', 'color': SIGNAL_COLORS['HOLD'], 'text': 'HOLD'},
        }

        config = signal_config.get(self.signal, signal_config['HOLD'])

        # Build display text
        display_text = f"{config['icon']} {config['text']}"

        if self.confidence > 0:
            display_text += f" ({self.confidence:.0%})"

        self.setText(display_text)

        # Apply styling
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {config['color']};
                color: #FFFFFF;
                border: none;
                border-radius: 6px;
                padding: 4px 12px;
            }}
        """)

    def set_signal(self, signal: str, confidence: float = 0.0):
        """
        Update the signal.

        Args:
            signal: Signal type ("BUY", "SELL", "HOLD")
            confidence: Signal confidence (0.0 to 1.0)
        """
        self.signal = signal.upper()
        self.confidence = confidence
        self._update_display()

    def get_signal(self) -> str:
        """Get current signal."""
        return self.signal

    def get_confidence(self) -> float:
        """Get current confidence."""
        return self.confidence


class StatusBadge(QLabel):
    """
    A badge widget for displaying status indicators.

    Used for connection status, market status, etc.
    """

    def __init__(self, status: str = "DISCONNECTED", parent=None):
        super().__init__(parent)
        self.status = status.upper()

        self._setup_ui()
        self._update_display()

    def _setup_ui(self):
        """Setup the badge UI."""
        font = QFont()
        font.setFamilies(['Inter', 'SF Pro Display', 'Segoe UI'])
        font.setPointSize(10)
        font.setWeight(QFont.Weight.Medium)
        self.setFont(font)

        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFixedHeight(28)
        self.setMinimumWidth(100)

    def _update_display(self):
        """Update the badge display based on status."""
        from app.styles import STATUS_COLORS

        # Get status icon and color
        status_config = {
            'CONNECTED': {'icon': '●', 'color': STATUS_COLORS['CONNECTED'], 'text': 'CONNECTED'},
            'DISCONNECTED': {'icon': '●', 'color': STATUS_COLORS['DISCONNECTED'], 'text': 'DISCONNECTED'},
            'CONNECTING': {'icon': '●', 'color': STATUS_COLORS['CONNECTING'], 'text': 'CONNECTING...'},
            'MARKET_OPEN': {'icon': '●', 'color': COLORS['success'], 'text': 'MARKET OPEN'},
            'MARKET_CLOSED': {'icon': '●', 'color': COLORS['negative'], 'text': 'MARKET CLOSED'},
            'PRE_MARKET': {'icon': '●', 'color': COLORS['warning'], 'text': 'PRE-MARKET'},
            'AFTER_HOURS': {'icon': '●', 'color': COLORS['warning'], 'text': 'AFTER-HOURS'},
        }

        config = status_config.get(self.status, {
            'icon': '●',
            'color': COLORS['text_secondary'],
            'text': self.status
        })

        # Build display text
        display_text = f"{config['icon']} {config['text']}"
        self.setText(display_text)

        # Apply styling with semi-transparent background
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {COLORS['bg_elevated']};
                color: {config['color']};
                border: 1px solid {config['color']};
                border-radius: 14px;
                padding: 4px 12px;
            }}
        """)

    def set_status(self, status: str):
        """
        Update the status.

        Args:
            status: Status text
        """
        self.status = status.upper()
        self._update_display()

    def get_status(self) -> str:
        """Get current status."""
        return self.status

"""Trading page with charts and order entry."""

import logging
from typing import Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QPushButton, QLineEdit, QLabel, QComboBox,
    QGroupBox, QFormLayout, QSpinBox, QDoubleSpinBox
)
from PyQt6.QtCore import Qt, pyqtSignal

from app.widgets import ChartPanel, SignalBadge
from app.styles.colors import COLORS
from core import OrderSide, OrderType


class TradingPage(QWidget):
    """
    Trading page with live charts and order entry.

    Features:
    - Symbol search and selection
    - Live price chart with indicators
    - Order entry panel (market/limit orders)
    - Technical signals display
    - Quick buy/sell buttons
    """

    symbol_changed = pyqtSignal(str)  # symbol selected
    order_requested = pyqtSignal(dict)  # order parameters
    data_refresh_requested = pyqtSignal(str)  # symbol to refresh

    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)

        self.current_symbol: Optional[str] = None
        self.current_price: float = 0.0

        self._init_ui()

    def _init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Main splitter (chart | order entry panel)
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left: Chart panel
        self.chart_panel = ChartPanel()
        self.chart_panel.timeframe_changed.connect(self._on_timeframe_changed)
        splitter.addWidget(self.chart_panel)

        # Right: Order entry and info panel
        right_panel = self._create_right_panel()
        splitter.addWidget(right_panel)

        # Set size ratio (chart takes 70%, panel takes 30%)
        splitter.setSizes([700, 300])

        layout.addWidget(splitter)

    def _create_right_panel(self) -> QWidget:
        """Create the right panel with symbol search and order entry."""
        panel = QWidget()
        panel.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['bg_secondary']};
            }}
        """)
        panel.setMaximumWidth(400)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # Symbol search
        search_group = self._create_symbol_search()
        layout.addWidget(search_group)

        # Current price display
        self.price_display = self._create_price_display()
        layout.addWidget(self.price_display)

        # Technical signals
        signals_group = self._create_signals_panel()
        layout.addWidget(signals_group)

        # Order entry
        order_group = self._create_order_entry()
        layout.addWidget(order_group)

        layout.addStretch()

        return panel

    def _create_symbol_search(self) -> QGroupBox:
        """Create symbol search group."""
        group = QGroupBox("Symbol")
        group.setStyleSheet(f"""
            QGroupBox {{
                color: {COLORS['text_primary']};
                font-weight: 600;
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 12px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 4px;
            }}
        """)

        layout = QVBoxLayout(group)

        # Symbol input
        input_layout = QHBoxLayout()

        self.symbol_input = QLineEdit()
        self.symbol_input.setPlaceholderText("Enter symbol (e.g., AAPL)")
        self.symbol_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {COLORS['bg_elevated']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
            }}
            QLineEdit:focus {{
                border-color: {COLORS['accent_blue']};
            }}
        """)
        self.symbol_input.returnPressed.connect(self._on_symbol_search)
        input_layout.addWidget(self.symbol_input)

        search_btn = QPushButton("Search")
        search_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['accent_blue']};
                color: {COLORS['text_primary']};
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {COLORS['positive']};
            }}
        """)
        search_btn.clicked.connect(self._on_symbol_search)
        input_layout.addWidget(search_btn)

        layout.addLayout(input_layout)

        return group

    def _create_price_display(self) -> QWidget:
        """Create current price display."""
        widget = QWidget()
        widget.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['bg_elevated']};
                border-radius: 8px;
                padding: 16px;
            }}
        """)

        layout = QVBoxLayout(widget)
        layout.setSpacing(4)

        # Price label
        self.price_label = QLabel("--")
        self.price_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text_primary']};
                font-size: 32px;
                font-weight: 700;
            }}
        """)
        self.price_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.price_label)

        # Change label
        self.change_label = QLabel("--")
        self.change_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text_secondary']};
                font-size: 14px;
            }}
        """)
        self.change_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.change_label)

        return widget

    def _create_signals_panel(self) -> QGroupBox:
        """Create technical signals panel."""
        group = QGroupBox("Technical Signals")
        group.setStyleSheet(f"""
            QGroupBox {{
                color: {COLORS['text_primary']};
                font-weight: 600;
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 12px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 4px;
            }}
        """)

        layout = QVBoxLayout(group)
        layout.setSpacing(8)

        # Signal badges
        signals_layout = QHBoxLayout()
        signals_layout.setSpacing(8)

        self.rsi_badge = SignalBadge("RSI")
        self.macd_badge = SignalBadge("MACD")
        self.ma_badge = SignalBadge("MA")

        signals_layout.addWidget(self.rsi_badge)
        signals_layout.addWidget(self.macd_badge)
        signals_layout.addWidget(self.ma_badge)

        layout.addLayout(signals_layout)

        return group

    def _create_order_entry(self) -> QGroupBox:
        """Create order entry panel."""
        group = QGroupBox("Quick Order")
        group.setStyleSheet(f"""
            QGroupBox {{
                color: {COLORS['text_primary']};
                font-weight: 600;
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 12px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 4px;
            }}
        """)

        layout = QFormLayout(group)
        layout.setSpacing(12)

        # Order type
        self.order_type_combo = QComboBox()
        self.order_type_combo.addItems(["Market", "Limit"])
        self.order_type_combo.currentTextChanged.connect(self._on_order_type_changed)
        layout.addRow("Type:", self.order_type_combo)

        # Quantity
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setMinimum(1)
        self.quantity_spin.setMaximum(10000)
        self.quantity_spin.setValue(1)
        layout.addRow("Quantity:", self.quantity_spin)

        # Limit price (hidden by default)
        self.limit_price_spin = QDoubleSpinBox()
        self.limit_price_spin.setMinimum(0.01)
        self.limit_price_spin.setMaximum(100000.0)
        self.limit_price_spin.setDecimals(2)
        self.limit_price_spin.setSingleStep(0.01)
        self.limit_price_spin.setPrefix("$ ")
        self.limit_price_label = QLabel("Limit Price:")
        layout.addRow(self.limit_price_label, self.limit_price_spin)
        self.limit_price_label.hide()
        self.limit_price_spin.hide()

        # Buy/Sell buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(12)

        self.buy_btn = QPushButton("BUY")
        self.buy_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['positive']};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px;
                font-weight: 600;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: #00D67E;
            }}
            QPushButton:disabled {{
                background-color: {COLORS['bg_elevated']};
                color: {COLORS['text_secondary']};
            }}
        """)
        self.buy_btn.clicked.connect(lambda: self._on_quick_order(OrderSide.BUY))
        self.buy_btn.setEnabled(False)
        buttons_layout.addWidget(self.buy_btn)

        self.sell_btn = QPushButton("SELL")
        self.sell_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['negative']};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px;
                font-weight: 600;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: #FF6257;
            }}
            QPushButton:disabled {{
                background-color: {COLORS['bg_elevated']};
                color: {COLORS['text_secondary']};
            }}
        """)
        self.sell_btn.clicked.connect(lambda: self._on_quick_order(OrderSide.SELL))
        self.sell_btn.setEnabled(False)
        buttons_layout.addWidget(self.sell_btn)

        layout.addRow(buttons_layout)

        return group

    def _on_symbol_search(self):
        """Handle symbol search."""
        symbol = self.symbol_input.text().strip().upper()

        if not symbol:
            return

        self.current_symbol = symbol
        self.symbol_changed.emit(symbol)
        self.data_refresh_requested.emit(symbol)

        # Enable order buttons
        self.buy_btn.setEnabled(True)
        self.sell_btn.setEnabled(True)

    def _on_timeframe_changed(self, timeframe: str):
        """Handle timeframe change."""
        if self.current_symbol:
            self.data_refresh_requested.emit(self.current_symbol)

    def _on_order_type_changed(self, order_type: str):
        """Handle order type change."""
        if order_type == "Limit":
            self.limit_price_label.show()
            self.limit_price_spin.show()
            self.limit_price_spin.setValue(self.current_price)
        else:
            self.limit_price_label.hide()
            self.limit_price_spin.hide()

    def _on_quick_order(self, side: OrderSide):
        """Handle quick order button click."""
        if not self.current_symbol:
            return

        order_type_text = self.order_type_combo.currentText()
        order_type = OrderType.MARKET if order_type_text == "Market" else OrderType.LIMIT

        order_params = {
            'symbol': self.current_symbol,
            'side': side,
            'quantity': float(self.quantity_spin.value()),
            'order_type': order_type,
        }

        if order_type == OrderType.LIMIT:
            order_params['limit_price'] = self.limit_price_spin.value()

        self.order_requested.emit(order_params)

    def update_data(self, symbol: str, data: dict):
        """
        Update the trading page with new data.

        Args:
            symbol: Stock symbol
            data: Data dictionary with 'historical' and 'quote'
        """
        if symbol != self.current_symbol:
            return

        # Update chart
        self.chart_panel.update_data(symbol, data)

        # Update price display
        quote = data.get('quote', {})
        price = quote.get('price', 0.0)
        change = quote.get('change', 0.0)
        change_pct = quote.get('change_percent', 0.0)

        self.current_price = price

        # Update price label
        self.price_label.setText(f"${price:.2f}")

        # Update change label with color
        change_text = f"{change:+.2f} ({change_pct:+.2f}%)"
        color = COLORS['positive'] if change >= 0 else COLORS['negative']
        self.change_label.setText(change_text)
        self.change_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: 14px;
                font-weight: 600;
            }}
        """)

        # Update limit price default
        if self.order_type_combo.currentText() == "Limit":
            self.limit_price_spin.setValue(price)

        # Update technical signals
        self._update_signals(data)

    def _update_signals(self, data: dict):
        """Update technical signal badges."""
        df = data.get('historical')
        if df is None or len(df) == 0:
            return

        latest = df.iloc[-1]

        # RSI signal
        if 'rsi' in df.columns and pd.notna(latest['rsi']):
            rsi = latest['rsi']
            if rsi > 70:
                self.rsi_badge.set_signal("SELL", f"RSI: {rsi:.1f}")
            elif rsi < 30:
                self.rsi_badge.set_signal("BUY", f"RSI: {rsi:.1f}")
            else:
                self.rsi_badge.set_signal("HOLD", f"RSI: {rsi:.1f}")

        # MACD signal
        if 'macd' in df.columns and 'macd_signal' in df.columns:
            macd = latest['macd']
            signal = latest['macd_signal']
            if pd.notna(macd) and pd.notna(signal):
                if macd > signal:
                    self.macd_badge.set_signal("BUY", "Bullish")
                else:
                    self.macd_badge.set_signal("SELL", "Bearish")

        # Moving Average signal
        if 'sma_20' in df.columns and 'sma_50' in df.columns:
            close = latest['close']
            sma_20 = latest['sma_20']
            sma_50 = latest['sma_50']
            if pd.notna(sma_20) and pd.notna(sma_50):
                if close > sma_20 > sma_50:
                    self.ma_badge.set_signal("BUY", "Strong Uptrend")
                elif close < sma_20 < sma_50:
                    self.ma_badge.set_signal("SELL", "Strong Downtrend")
                else:
                    self.ma_badge.set_signal("HOLD", "Mixed")

    def clear(self):
        """Clear the trading page."""
        self.current_symbol = None
        self.current_price = 0.0
        self.symbol_input.clear()
        self.chart_panel.clear()
        self.price_label.setText("--")
        self.change_label.setText("--")
        self.buy_btn.setEnabled(False)
        self.sell_btn.setEnabled(False)


# Missing pandas import
import pandas as pd

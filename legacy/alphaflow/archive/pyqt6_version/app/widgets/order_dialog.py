"""Order entry dialog for placing trades."""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QDoubleSpinBox, QSpinBox,
    QGroupBox, QFormLayout, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from app.styles import COLORS
from core import OrderSide, OrderType, TimeInForce


class OrderEntryDialog(QDialog):
    """
    Dialog for entering trade orders.

    Supports:
    - Market orders
    - Limit orders
    - Buy/Sell selection
    - Quantity input
    - Price input (for limit orders)
    """

    order_submitted = pyqtSignal(dict)  # order_params

    def __init__(self, symbol: str = "", current_price: float = 0.0, parent=None):
        super().__init__(parent)
        self.symbol = symbol
        self.current_price = current_price

        self._setup_ui()
        self._apply_styling()
        self._connect_signals()

    def _setup_ui(self):
        """Setup the dialog UI."""
        self.setWindowTitle("New Order")
        self.setModal(True)
        self.setMinimumWidth(400)

        layout = QVBoxLayout()
        layout.setSpacing(16)

        # Title
        title = QLabel("Place Order")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setWeight(QFont.Weight.Bold)
        title.setFont(title_font)
        layout.addWidget(title)

        # Order details form
        form_group = QGroupBox("Order Details")
        form_layout = QFormLayout()
        form_layout.setSpacing(12)

        # Symbol
        self.symbol_input = QLineEdit(self.symbol)
        self.symbol_input.setPlaceholderText("e.g., AAPL")
        form_layout.addRow("Symbol:", self.symbol_input)

        # Side (Buy/Sell)
        self.side_combo = QComboBox()
        self.side_combo.addItems(["BUY", "SELL"])
        form_layout.addRow("Side:", self.side_combo)

        # Order type
        self.order_type_combo = QComboBox()
        self.order_type_combo.addItems(["MARKET", "LIMIT"])
        form_layout.addRow("Order Type:", self.order_type_combo)

        # Quantity
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setMinimum(1)
        self.quantity_spin.setMaximum(10000)
        self.quantity_spin.setValue(100)
        self.quantity_spin.setSuffix(" shares")
        form_layout.addRow("Quantity:", self.quantity_spin)

        # Limit price (only for limit orders)
        self.price_spin = QDoubleSpinBox()
        self.price_spin.setMinimum(0.01)
        self.price_spin.setMaximum(100000.00)
        self.price_spin.setDecimals(2)
        self.price_spin.setPrefix("$ ")
        self.price_spin.setValue(self.current_price if self.current_price > 0 else 100.00)
        self.price_label = QLabel("Limit Price:")
        form_layout.addRow(self.price_label, self.price_spin)

        # Time in force
        self.tif_combo = QComboBox()
        self.tif_combo.addItems(["DAY", "GTC", "IOC", "FOK"])
        form_layout.addRow("Time in Force:", self.tif_combo)

        form_group.setLayout(form_layout)
        layout.addWidget(form_group)

        # Order summary
        self.summary_label = QLabel()
        self.summary_label.setWordWrap(True)
        self.summary_label.setStyleSheet(f"""
            QLabel {{
                background-color: {COLORS['bg_elevated']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                padding: 12px;
                color: {COLORS['text_secondary']};
            }}
        """)
        self._update_summary()
        layout.addWidget(self.summary_label)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)

        self.submit_button = QPushButton("Place Order")
        self.submit_button.setObjectName("BuyButton")  # Green button style
        self.submit_button.clicked.connect(self._on_submit)

        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.submit_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def _apply_styling(self):
        """Apply dialog styling."""
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['bg_primary']};
            }}
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
                subcontrol-position: top left;
                left: 12px;
                padding: 0 8px;
            }}
        """)

    def _connect_signals(self):
        """Connect signals."""
        self.order_type_combo.currentTextChanged.connect(self._on_order_type_changed)
        self.side_combo.currentTextChanged.connect(self._update_summary)
        self.symbol_input.textChanged.connect(self._update_summary)
        self.quantity_spin.valueChanged.connect(self._update_summary)
        self.price_spin.valueChanged.connect(self._update_summary)

        # Initial state
        self._on_order_type_changed(self.order_type_combo.currentText())

    def _on_order_type_changed(self, order_type: str):
        """Handle order type change."""
        is_limit = order_type == "LIMIT"

        self.price_label.setVisible(is_limit)
        self.price_spin.setVisible(is_limit)

        self._update_summary()

    def _update_summary(self):
        """Update order summary text."""
        symbol = self.symbol_input.text().strip().upper()
        side = self.side_combo.currentText()
        quantity = self.quantity_spin.value()
        order_type = self.order_type_combo.currentText()

        if order_type == "MARKET":
            summary = f"{side} {quantity} shares of {symbol or '[SYMBOL]'} at MARKET price"
        else:
            price = self.price_spin.value()
            total = quantity * price
            summary = f"{side} {quantity} shares of {symbol or '[SYMBOL]'} at ${price:.2f} (Total: ${total:,.2f})"

        self.summary_label.setText(f"📋 Order Summary:\n{summary}")

        # Update button color based on side
        if side == "BUY":
            self.submit_button.setObjectName("BuyButton")
        else:
            self.submit_button.setObjectName("SellButton")

        self.submit_button.setStyleSheet("")  # Force style refresh

    def _on_submit(self):
        """Handle order submission."""
        symbol = self.symbol_input.text().strip().upper()

        # Validation
        if not symbol:
            QMessageBox.warning(self, "Invalid Input", "Please enter a symbol")
            return

        if len(symbol) > 5:
            QMessageBox.warning(self, "Invalid Input", "Symbol appears invalid")
            return

        # Confirmation
        order_type = self.order_type_combo.currentText()
        side = self.side_combo.currentText()
        quantity = self.quantity_spin.value()

        if order_type == "MARKET":
            msg = f"Place MARKET {side} order for {quantity} shares of {symbol}?"
        else:
            price = self.price_spin.value()
            msg = f"Place LIMIT {side} order for {quantity} shares of {symbol} at ${price:.2f}?"

        reply = QMessageBox.question(
            self,
            "Confirm Order",
            msg,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Build order parameters
            order_params = {
                'symbol': symbol,
                'side': OrderSide.BUY if side == "BUY" else OrderSide.SELL,
                'quantity': quantity,
                'order_type': OrderType.MARKET if order_type == "MARKET" else OrderType.LIMIT,
                'time_in_force': TimeInForce[self.tif_combo.currentText()],
            }

            if order_type == "LIMIT":
                order_params['limit_price'] = self.price_spin.value()

            self.order_submitted.emit(order_params)
            self.accept()

    def set_symbol(self, symbol: str, price: float = 0.0):
        """
        Set the symbol and current price.

        Args:
            symbol: Stock symbol
            price: Current price
        """
        self.symbol = symbol
        self.current_price = price
        self.symbol_input.setText(symbol)

        if price > 0:
            self.price_spin.setValue(price)

        self._update_summary()

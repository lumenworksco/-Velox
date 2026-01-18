"""Strategy management page for deploying and monitoring automated trading strategies."""

import logging
from typing import Optional, Dict, List
from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QLabel, QPushButton, QComboBox, QListWidget,
    QListWidgetItem, QTextEdit, QScrollArea,
    QCheckBox, QSpinBox, QDoubleSpinBox, QMessageBox,
    QFormLayout, QSplitter
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont

from app.styles.colors import COLORS
from app.widgets import MetricCard, StatusBadge, BloombergDataGrid


class StrategyCard(QWidget):
    """Card widget for displaying a single strategy."""

    start_requested = pyqtSignal(str)  # strategy_id
    stop_requested = pyqtSignal(str)  # strategy_id
    edit_requested = pyqtSignal(str)  # strategy_id
    delete_requested = pyqtSignal(str)  # strategy_id

    def __init__(self, strategy_data: dict, parent=None):
        super().__init__(parent)
        self.strategy_data = strategy_data
        self.strategy_id = strategy_data['id']

        self._init_ui()

    def _init_ui(self):
        """Initialize the UI."""
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['bg_secondary']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
            }}
        """)
        self.setFixedHeight(180)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Header row
        header_layout = QHBoxLayout()

        # Strategy name
        name_label = QLabel(self.strategy_data['name'])
        name_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text_primary']};
                font-size: 16px;
                font-weight: 700;
            }}
        """)
        header_layout.addWidget(name_label)

        header_layout.addStretch()

        # Status badge
        self.status_badge = StatusBadge(self.strategy_data['status'])
        header_layout.addWidget(self.status_badge)

        layout.addLayout(header_layout)

        # Description
        desc_label = QLabel(self.strategy_data.get('description', 'No description'))
        desc_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)

        # Stats row
        stats_layout = QHBoxLayout()

        # Symbols
        symbols_label = QLabel(f"Symbols: {', '.join(self.strategy_data.get('symbols', []))}")
        symbols_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 11px;")
        stats_layout.addWidget(symbols_label)

        stats_layout.addStretch()

        # P&L
        pnl = self.strategy_data.get('total_pnl', 0.0)
        pnl_color = COLORS['positive'] if pnl >= 0 else COLORS['negative']
        pnl_label = QLabel(f"P&L: ${pnl:+.2f}")
        pnl_label.setStyleSheet(f"color: {pnl_color}; font-weight: 600; font-size: 12px;")
        stats_layout.addWidget(pnl_label)

        layout.addLayout(stats_layout)

        # Actions row
        actions_layout = QHBoxLayout()

        # Start/Stop button
        self.toggle_button = QPushButton("Start" if self.strategy_data['status'] == 'STOPPED' else "Stop")
        self.toggle_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['positive'] if self.strategy_data['status'] == 'STOPPED' else COLORS['negative']};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: 600;
            }}
        """)
        self.toggle_button.clicked.connect(self._on_toggle)
        actions_layout.addWidget(self.toggle_button)

        # Edit button
        edit_btn = QPushButton("Edit")
        edit_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['accent_blue']};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
            }}
        """)
        edit_btn.clicked.connect(lambda: self.edit_requested.emit(self.strategy_id))
        actions_layout.addWidget(edit_btn)

        # Delete button
        delete_btn = QPushButton("Delete")
        delete_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['bg_elevated']};
                color: {COLORS['text_secondary']};
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
                padding: 6px 12px;
            }}
        """)
        delete_btn.clicked.connect(lambda: self.delete_requested.emit(self.strategy_id))
        actions_layout.addWidget(delete_btn)

        actions_layout.addStretch()

        layout.addLayout(actions_layout)

    def _on_toggle(self):
        """Handle start/stop toggle."""
        if self.strategy_data['status'] == 'STOPPED':
            self.start_requested.emit(self.strategy_id)
        else:
            self.stop_requested.emit(self.strategy_id)

    def update_status(self, status: str):
        """Update strategy status."""
        self.strategy_data['status'] = status
        self.status_badge.set_status(status)
        self.toggle_button.setText("Start" if status == 'STOPPED' else "Stop")
        bg_color = COLORS['positive'] if status == 'STOPPED' else COLORS['negative']
        self.toggle_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg_color};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: 600;
            }}
        """)


class StrategyPage(QWidget):
    """
    Strategy management page for automated trading.

    Features:
    - List of deployed strategies
    - Start/stop strategy execution
    - Create new strategies
    - Edit existing strategies
    - Monitor strategy performance
    - View strategy logs
    """

    strategy_started = pyqtSignal(str)  # strategy_id
    strategy_stopped = pyqtSignal(str)  # strategy_id

    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)

        # Mock strategies data
        self.strategies: Dict[str, dict] = {
            'strategy_1': {
                'id': 'strategy_1',
                'name': 'MA Crossover AAPL',
                'description': '20/50 MA crossover strategy on AAPL',
                'symbols': ['AAPL'],
                'status': 'RUNNING',
                'total_pnl': 1250.75,
                'trades_today': 3,
            },
            'strategy_2': {
                'id': 'strategy_2',
                'name': 'RSI Mean Reversion',
                'description': 'Buy oversold, sell overbought on tech stocks',
                'symbols': ['MSFT', 'GOOGL', 'NVDA'],
                'status': 'STOPPED',
                'total_pnl': -230.50,
                'trades_today': 0,
            },
        }

        self._init_ui()

    def _init_ui(self):
        """Initialize the user interface."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Main splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left: Strategy list
        left_panel = self._create_strategy_list_panel()
        splitter.addWidget(left_panel)

        # Right: Strategy details and logs
        right_panel = self._create_details_panel()
        splitter.addWidget(right_panel)

        # Set size ratio (50/50)
        splitter.setSizes([500, 500])

        layout.addWidget(splitter)

    def _create_strategy_list_panel(self) -> QWidget:
        """Create strategy list panel."""
        panel = QWidget()
        panel.setStyleSheet(f"background-color: {COLORS['bg_secondary']};")

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # Header
        header_layout = QHBoxLayout()

        title = QLabel("Active Strategies")
        title.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text_primary']};
                font-size: 18px;
                font-weight: 700;
            }}
        """)
        header_layout.addWidget(title)

        header_layout.addStretch()

        # New strategy button
        new_btn = QPushButton("+ New Strategy")
        new_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['positive']};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 600;
            }}
        """)
        new_btn.clicked.connect(self._on_new_strategy)
        header_layout.addWidget(new_btn)

        layout.addLayout(header_layout)

        # Summary metrics
        summary_layout = QHBoxLayout()

        total_strategies = len(self.strategies)
        running = sum(1 for s in self.strategies.values() if s['status'] == 'RUNNING')
        total_pnl = sum(s['total_pnl'] for s in self.strategies.values())

        self.total_strategies_label = QLabel(f"{total_strategies} Total")
        self.total_strategies_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        summary_layout.addWidget(self.total_strategies_label)

        self.running_label = QLabel(f"{running} Running")
        self.running_label.setStyleSheet(f"color: {COLORS['positive']}; font-weight: 600;")
        summary_layout.addWidget(self.running_label)

        pnl_color = COLORS['positive'] if total_pnl >= 0 else COLORS['negative']
        self.total_pnl_label = QLabel(f"Total P&L: ${total_pnl:+.2f}")
        self.total_pnl_label.setStyleSheet(f"color: {pnl_color}; font-weight: 600;")
        summary_layout.addWidget(self.total_pnl_label)

        summary_layout.addStretch()

        layout.addLayout(summary_layout)

        # Scroll area for strategy cards
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)

        scroll_content = QWidget()
        self.strategies_layout = QVBoxLayout(scroll_content)
        self.strategies_layout.setSpacing(12)

        # Add strategy cards
        self._refresh_strategy_cards()

        self.strategies_layout.addStretch()

        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

        return panel

    def _create_details_panel(self) -> QWidget:
        """Create strategy details and logs panel."""
        panel = QWidget()
        panel.setStyleSheet(f"background-color: {COLORS['bg_primary']};")

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # Performance metrics
        title = QLabel("Performance Overview")
        title.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text_primary']};
                font-size: 18px;
                font-weight: 700;
            }}
        """)
        layout.addWidget(title)

        metrics_layout = QHBoxLayout()

        self.trades_today_card = MetricCard("Trades Today", "0", 0.0)
        self.active_positions_card = MetricCard("Active Positions", "0", 0.0)
        self.daily_pnl_card = MetricCard("Daily P&L", "$0.00", 0.0)

        metrics_layout.addWidget(self.trades_today_card)
        metrics_layout.addWidget(self.active_positions_card)
        metrics_layout.addWidget(self.daily_pnl_card)

        layout.addLayout(metrics_layout)

        # Recent trades
        trades_label = QLabel("Recent Trades")
        trades_label.setStyleSheet(f"color: {COLORS['text_primary']}; font-weight: 600;")
        layout.addWidget(trades_label)

        self.trades_grid = BloombergDataGrid()
        self.trades_grid.set_columns([
            'Time', 'Strategy', 'Symbol', 'Side', 'Quantity', 'Price', 'Status'
        ])
        layout.addWidget(self.trades_grid)

        # Strategy logs
        logs_label = QLabel("Strategy Logs")
        logs_label.setStyleSheet(f"color: {COLORS['text_primary']}; font-weight: 600;")
        layout.addWidget(logs_label)

        self.logs_text = QTextEdit()
        self.logs_text.setReadOnly(True)
        self.logs_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: {COLORS['bg_elevated']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                padding: 12px;
                font-family: monospace;
                font-size: 11px;
            }}
        """)
        self.logs_text.setMaximumHeight(200)
        layout.addWidget(self.logs_text)

        return panel

    def _refresh_strategy_cards(self):
        """Refresh the strategy cards display."""
        # Clear existing cards
        while self.strategies_layout.count() > 1:  # Keep the stretch
            item = self.strategies_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Add cards for each strategy
        for strategy_data in self.strategies.values():
            card = StrategyCard(strategy_data)
            card.start_requested.connect(self._on_start_strategy)
            card.stop_requested.connect(self._on_stop_strategy)
            card.edit_requested.connect(self._on_edit_strategy)
            card.delete_requested.connect(self._on_delete_strategy)
            self.strategies_layout.insertWidget(self.strategies_layout.count() - 1, card)

    def _on_new_strategy(self):
        """Handle new strategy creation."""
        # This would open a strategy creation dialog
        QMessageBox.information(
            self,
            "New Strategy",
            "Strategy creation wizard will be implemented here.\n\n"
            "You'll be able to:\n"
            "- Choose strategy type\n"
            "- Configure parameters\n"
            "- Select symbols\n"
            "- Set risk limits"
        )

    def _on_start_strategy(self, strategy_id: str):
        """Handle strategy start request."""
        if strategy_id in self.strategies:
            self.strategies[strategy_id]['status'] = 'RUNNING'
            self._refresh_strategy_cards()
            self._add_log(f"Strategy '{self.strategies[strategy_id]['name']}' started")
            self.strategy_started.emit(strategy_id)

    def _on_stop_strategy(self, strategy_id: str):
        """Handle strategy stop request."""
        if strategy_id in self.strategies:
            self.strategies[strategy_id]['status'] = 'STOPPED'
            self._refresh_strategy_cards()
            self._add_log(f"Strategy '{self.strategies[strategy_id]['name']}' stopped")
            self.strategy_stopped.emit(strategy_id)

    def _on_edit_strategy(self, strategy_id: str):
        """Handle strategy edit request."""
        QMessageBox.information(
            self,
            "Edit Strategy",
            f"Editing strategy: {self.strategies[strategy_id]['name']}\n\n"
            "Strategy editor will be implemented here."
        )

    def _on_delete_strategy(self, strategy_id: str):
        """Handle strategy deletion."""
        if strategy_id in self.strategies:
            reply = QMessageBox.question(
                self,
                "Delete Strategy",
                f"Are you sure you want to delete '{self.strategies[strategy_id]['name']}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                del self.strategies[strategy_id]
                self._refresh_strategy_cards()
                self._add_log(f"Strategy deleted")

    def _add_log(self, message: str):
        """Add a log message."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.logs_text.append(log_entry)

    def add_trade(self, trade_data: dict):
        """Add a trade to the recent trades table."""
        self.trades_grid.add_row(trade_data)

        # Update metrics
        trades_count = self.trades_grid.rowCount()
        self.trades_today_card.set_value(str(trades_count), 0.0)

"""Backtest page for strategy testing and performance analysis."""

import logging
from typing import Optional, Dict, List
from datetime import datetime, timedelta
import pandas as pd

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QLabel, QPushButton, QComboBox, QDateEdit,
    QFormLayout, QTextEdit, QScrollArea, QSplitter,
    QProgressBar, QSpinBox, QDoubleSpinBox, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QDate, QThread
from PyQt6.QtCharts import QChart, QChartView, QLineSeries, QDateTimeAxis, QValueAxis
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush

from app.styles.colors import COLORS
from app.widgets import MetricCard, BloombergDataGrid
from core import BacktestEngine


class BacktestWorker(QThread):
    """Background worker for running backtests."""

    progress_updated = pyqtSignal(int, str)  # percentage, status_message
    backtest_complete = pyqtSignal(dict)  # results
    error_occurred = pyqtSignal(str)  # error_message

    def __init__(self, strategy_config: dict, backtest_params: dict):
        super().__init__()
        self.strategy_config = strategy_config
        self.backtest_params = backtest_params
        self.logger = logging.getLogger(__name__)

    def run(self):
        """Run the backtest."""
        try:
            self.progress_updated.emit(10, "Initializing backtest engine...")

            # Create backtest engine
            engine = BacktestEngine(
                initial_capital=self.backtest_params['initial_capital'],
                commission=self.backtest_params['commission']
            )

            self.progress_updated.emit(30, "Fetching historical data...")

            # Fetch data for symbols
            # This would integrate with DataController
            # For now, we'll simulate

            self.progress_updated.emit(50, "Running strategy...")

            # Run backtest
            results = engine.run_backtest(
                symbols=self.backtest_params['symbols'],
                start_date=str(self.backtest_params['start_date']),
                end_date=str(self.backtest_params['end_date']),
                strategy=self.strategy_config['type']
            )

            self.progress_updated.emit(100, "Backtest complete!")
            self.backtest_complete.emit(results)

        except Exception as e:
            self.logger.error(f"Backtest error: {e}")
            self.error_occurred.emit(str(e))


class BacktestPage(QWidget):
    """
    Backtest page for strategy testing and performance analysis.

    Features:
    - Strategy configuration
    - Date range selection
    - Symbol selection
    - Performance metrics
    - Equity curve chart
    - Trade list
    - Drawdown analysis
    """

    backtest_started = pyqtSignal(dict)  # backtest parameters

    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)

        self.current_results: Optional[dict] = None
        self.backtest_worker: Optional[BacktestWorker] = None

        self._init_ui()

    def _init_ui(self):
        """Initialize the user interface."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Main splitter (configuration | results)
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left: Configuration panel
        config_panel = self._create_config_panel()
        splitter.addWidget(config_panel)

        # Right: Results panel
        results_panel = self._create_results_panel()
        splitter.addWidget(results_panel)

        # Set size ratio (30% config, 70% results)
        splitter.setSizes([300, 700])

        layout.addWidget(splitter)

    def _create_config_panel(self) -> QWidget:
        """Create backtest configuration panel."""
        panel = QWidget()
        panel.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['bg_secondary']};
            }}
        """)
        panel.setMaximumWidth(400)

        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # Title
        title = QLabel("Backtest Configuration")
        title.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text_primary']};
                font-size: 18px;
                font-weight: 700;
            }}
        """)
        layout.addWidget(title)

        # Strategy selection
        strategy_group = self._create_strategy_group()
        layout.addWidget(strategy_group)

        # Date range
        date_group = self._create_date_range_group()
        layout.addWidget(date_group)

        # Symbols
        symbols_group = self._create_symbols_group()
        layout.addWidget(symbols_group)

        # Parameters
        params_group = self._create_parameters_group()
        layout.addWidget(params_group)

        # Run button
        self.run_button = QPushButton("Run Backtest")
        self.run_button.setStyleSheet(f"""
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
        self.run_button.clicked.connect(self._on_run_backtest)
        layout.addWidget(self.run_button)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
                text-align: center;
                background-color: {COLORS['bg_elevated']};
            }}
            QProgressBar::chunk {{
                background-color: {COLORS['positive']};
            }}
        """)
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Status label
        self.status_label = QLabel("")
        self.status_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
        self.status_label.setWordWrap(True)
        self.status_label.setVisible(False)
        layout.addWidget(self.status_label)

        layout.addStretch()

        scroll.setWidget(content)

        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(0, 0, 0, 0)
        panel_layout.addWidget(scroll)

        return panel

    def _create_strategy_group(self) -> QGroupBox:
        """Create strategy selection group."""
        group = QGroupBox("Strategy")
        self._style_group(group)

        layout = QFormLayout(group)
        layout.setSpacing(12)

        # Strategy selector
        self.strategy_combo = QComboBox()
        self.strategy_combo.addItems([
            "Moving Average Crossover",
            "RSI Mean Reversion",
            "MACD Momentum",
            "Bollinger Band Breakout",
            "Multi-Timeframe Trend",
            "Custom Strategy"
        ])
        self._style_combo(self.strategy_combo)
        layout.addRow("Type:", self.strategy_combo)

        return group

    def _create_date_range_group(self) -> QGroupBox:
        """Create date range selection group."""
        group = QGroupBox("Date Range")
        self._style_group(group)

        layout = QFormLayout(group)
        layout.setSpacing(12)

        # Start date
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate().addYears(-1))
        self.start_date.setCalendarPopup(True)
        self._style_date_edit(self.start_date)
        layout.addRow("Start:", self.start_date)

        # End date
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setCalendarPopup(True)
        self._style_date_edit(self.end_date)
        layout.addRow("End:", self.end_date)

        return group

    def _create_symbols_group(self) -> QGroupBox:
        """Create symbols selection group."""
        group = QGroupBox("Symbols")
        self._style_group(group)

        layout = QVBoxLayout(group)
        layout.setSpacing(12)

        # Symbols text edit
        self.symbols_text = QTextEdit()
        self.symbols_text.setPlaceholderText("Enter symbols, one per line\n(e.g., AAPL, MSFT, GOOGL)")
        self.symbols_text.setMaximumHeight(100)
        self.symbols_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: {COLORS['bg_elevated']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                padding: 8px;
                font-family: monospace;
            }}
        """)
        self.symbols_text.setText("AAPL\nMSFT\nGOOGL")
        layout.addWidget(self.symbols_text)

        return group

    def _create_parameters_group(self) -> QGroupBox:
        """Create backtest parameters group."""
        group = QGroupBox("Parameters")
        self._style_group(group)

        layout = QFormLayout(group)
        layout.setSpacing(12)

        # Initial capital
        self.initial_capital_spin = QDoubleSpinBox()
        self.initial_capital_spin.setMinimum(1000)
        self.initial_capital_spin.setMaximum(10000000)
        self.initial_capital_spin.setValue(100000)
        self.initial_capital_spin.setPrefix("$ ")
        self.initial_capital_spin.setDecimals(2)
        self._style_spinbox(self.initial_capital_spin)
        layout.addRow("Initial Capital:", self.initial_capital_spin)

        # Commission
        self.commission_spin = QDoubleSpinBox()
        self.commission_spin.setMinimum(0)
        self.commission_spin.setMaximum(1)
        self.commission_spin.setValue(0.001)
        self.commission_spin.setSingleStep(0.0001)
        self.commission_spin.setDecimals(4)
        self._style_spinbox(self.commission_spin)
        layout.addRow("Commission:", self.commission_spin)

        return group

    def _create_results_panel(self) -> QWidget:
        """Create results display panel."""
        panel = QWidget()
        panel.setStyleSheet(f"background-color: {COLORS['bg_primary']};")

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # Title
        title = QLabel("Backtest Results")
        title.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text_primary']};
                font-size: 18px;
                font-weight: 700;
            }}
        """)
        layout.addWidget(title)

        # Performance metrics
        metrics_layout = QHBoxLayout()

        self.total_return_card = MetricCard("Total Return", "--", 0.0)
        self.sharpe_ratio_card = MetricCard("Sharpe Ratio", "--", 0.0)
        self.max_drawdown_card = MetricCard("Max Drawdown", "--", 0.0)
        self.win_rate_card = MetricCard("Win Rate", "--", 0.0)

        metrics_layout.addWidget(self.total_return_card)
        metrics_layout.addWidget(self.sharpe_ratio_card)
        metrics_layout.addWidget(self.max_drawdown_card)
        metrics_layout.addWidget(self.win_rate_card)

        layout.addLayout(metrics_layout)

        # Equity curve chart
        chart_label = QLabel("Equity Curve")
        chart_label.setStyleSheet(f"color: {COLORS['text_primary']}; font-weight: 600;")
        layout.addWidget(chart_label)

        self.equity_chart_view = self._create_equity_chart()
        layout.addWidget(self.equity_chart_view)

        # Trades table
        trades_label = QLabel("Trade History")
        trades_label.setStyleSheet(f"color: {COLORS['text_primary']}; font-weight: 600;")
        layout.addWidget(trades_label)

        self.trades_grid = BloombergDataGrid()
        self.trades_grid.set_columns([
            'Date', 'Symbol', 'Side', 'Quantity', 'Entry Price',
            'Exit Price', 'P&L', 'P&L %', 'Duration'
        ])
        layout.addWidget(self.trades_grid)

        return panel

    def _create_equity_chart(self) -> QChartView:
        """Create equity curve chart."""
        self.equity_chart = QChart()
        self.equity_chart.setTitle("")
        self.equity_chart.setAnimationOptions(QChart.AnimationOption.NoAnimation)
        self.equity_chart.setBackgroundBrush(QBrush(QColor(COLORS['bg_secondary'])))
        self.equity_chart.setPlotAreaBackgroundBrush(QBrush(QColor(COLORS['bg_elevated'])))
        self.equity_chart.setPlotAreaBackgroundVisible(True)

        chart_view = QChartView(self.equity_chart)
        chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        chart_view.setMinimumHeight(300)

        return chart_view

    def _on_run_backtest(self):
        """Handle run backtest button click."""
        # Get symbols
        symbols_text = self.symbols_text.toPlainText()
        symbols = [s.strip().upper() for s in symbols_text.split('\n') if s.strip()]

        if not symbols:
            QMessageBox.warning(self, "No Symbols", "Please enter at least one symbol.")
            return

        # Get date range
        start_date = self.start_date.date().toPyDate()
        end_date = self.end_date.date().toPyDate()

        if start_date >= end_date:
            QMessageBox.warning(self, "Invalid Date Range", "Start date must be before end date.")
            return

        # Prepare backtest parameters
        strategy_config = {
            'type': self.strategy_combo.currentText(),
        }

        backtest_params = {
            'symbols': symbols,
            'start_date': start_date,
            'end_date': end_date,
            'initial_capital': self.initial_capital_spin.value(),
            'commission': self.commission_spin.value(),
        }

        # Disable run button
        self.run_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setVisible(True)
        self.status_label.setText("Starting backtest...")

        # Create and start worker
        self.backtest_worker = BacktestWorker(strategy_config, backtest_params)
        self.backtest_worker.progress_updated.connect(self._on_progress_updated)
        self.backtest_worker.backtest_complete.connect(self._on_backtest_complete)
        self.backtest_worker.error_occurred.connect(self._on_backtest_error)
        self.backtest_worker.start()

    def _on_progress_updated(self, percentage: int, message: str):
        """Handle backtest progress update."""
        self.progress_bar.setValue(percentage)
        self.status_label.setText(message)

    def _on_backtest_complete(self, results: dict):
        """Handle backtest completion."""
        self.current_results = results

        # Update metrics
        self._update_performance_metrics(results)

        # Update equity curve
        self._update_equity_curve(results)

        # Update trades table
        self._update_trades_table(results)

        # Re-enable run button
        self.run_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_label.setText("Backtest completed successfully!")

    def _on_backtest_error(self, error: str):
        """Handle backtest error."""
        QMessageBox.critical(self, "Backtest Error", f"Error running backtest:\n\n{error}")

        self.run_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_label.setText("Backtest failed.")

    def _update_performance_metrics(self, results: dict):
        """Update performance metric cards."""
        # Extract metrics from results
        total_return = results.get('total_return', 0.0)
        sharpe_ratio = results.get('sharpe_ratio', 0.0)
        max_drawdown = results.get('max_drawdown', 0.0)
        win_rate = results.get('win_rate', 0.0)

        # Update cards
        self.total_return_card.set_value(f"{total_return:+.2f}%", total_return)
        self.sharpe_ratio_card.set_value(f"{sharpe_ratio:.2f}", sharpe_ratio)
        self.max_drawdown_card.set_value(f"{max_drawdown:.2f}%", max_drawdown)
        self.win_rate_card.set_value(f"{win_rate:.1f}%", win_rate)

    def _update_equity_curve(self, results: dict):
        """Update equity curve chart."""
        equity_curve = results.get('equity_curve', [])

        if not equity_curve:
            return

        # Clear existing series
        self.equity_chart.removeAllSeries()

        # Create line series
        series = QLineSeries()
        series.setName("Portfolio Value")

        # Set color
        pen = QPen(QColor(COLORS['accent_alt']))
        pen.setWidth(2)
        series.setPen(pen)

        # Add data points
        for point in equity_curve:
            timestamp = point['timestamp'].timestamp() * 1000
            value = point['value']
            series.append(timestamp, value)

        # Add series to chart
        self.equity_chart.addSeries(series)

        # Create axes
        # (Implementation similar to chart_panel.py)
        self.equity_chart.createDefaultAxes()

    def _update_trades_table(self, results: dict):
        """Update trades table."""
        trades = results.get('trades', [])

        self.trades_grid.clear_data()

        for trade in trades:
            self.trades_grid.add_row({
                'Date': trade.get('exit_date', ''),
                'Symbol': trade.get('symbol', ''),
                'Side': trade.get('side', ''),
                'Quantity': trade.get('quantity', 0),
                'Entry Price': trade.get('entry_price', 0.0),
                'Exit Price': trade.get('exit_price', 0.0),
                'P&L': trade.get('pnl', 0.0),
                'P&L %': trade.get('pnl_percent', 0.0),
                'Duration': trade.get('duration', ''),
            })

    def _style_group(self, group: QGroupBox):
        """Apply styling to group box."""
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

    def _style_combo(self, combo: QComboBox):
        """Apply styling to combo box."""
        combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {COLORS['bg_elevated']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                padding: 8px 12px;
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox QAbstractItemView {{
                background-color: {COLORS['bg_elevated']};
                color: {COLORS['text_primary']};
                selection-background-color: {COLORS['accent_alt']};
            }}
        """)

    def _style_date_edit(self, date_edit: QDateEdit):
        """Apply styling to date edit."""
        date_edit.setStyleSheet(f"""
            QDateEdit {{
                background-color: {COLORS['bg_elevated']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                padding: 8px 12px;
            }}
        """)

    def _style_spinbox(self, spinbox):
        """Apply styling to spinbox."""
        spinbox.setStyleSheet(f"""
            QDoubleSpinBox, QSpinBox {{
                background-color: {COLORS['bg_elevated']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                padding: 8px 12px;
            }}
        """)

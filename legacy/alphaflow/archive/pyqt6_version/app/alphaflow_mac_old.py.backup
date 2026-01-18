

from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QMargins
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, QComboBox, QProgressBar, QScrollArea, QSplitter, QStyleFactory, QSpinBox, QDoubleSpinBox, QGroupBox, QFormLayout, QCheckBox, QMessageBox, QSettings, QGridLayout
)
from PyQt6.QtGui import QAction, QColor, QBrush, QPainter
from PyQt6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis
import sys
import logging
from datetime import datetime
from typing import Dict, List
import pandas as pd

COLORS = {
    'bg_main': '#181A1B',
    'bg_card': '#232526',
    'bg_card_hover': '#26282A',
    'bg_elevated': '#23272E',
    'border': '#31363B',
    'blue': '#3A8DFF',
    'blue_light': '#6EC1FF',
    'green': '#00D26A',
    'green_light': '#4EF6A5',
    'red': '#FF4757',
    'red_light': '#FF7B8A',
    'yellow': '#FFD166',
    'purple': '#A259FF',
    'text_primary': '#F3F6F9',
    'text_secondary': '#A0A4A8',
    'sidebar': '#1A1C1E',
    'sidebar_active': '#23272E',
    'sidebar_text': '#C7C9CB',
    'sidebar_icon': '#3A8DFF',
    'gradient_start': '#232526',
    'gradient_end': '#181A1B',
}

DARK_STYLESHEET = f"""
QWidget {{
    background-color: {COLORS['bg_main']};
    color: {COLORS['text_primary']};
    font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
    font-size: 14px;
}}
QFrame {{
    background-color: {COLORS['bg_card']};
    border: 1px solid {COLORS['border']};
    border-radius: 12px;
}}
QLabel {{
    color: {COLORS['text_primary']};
}}
QPushButton {{
    background-color: {COLORS['bg_elevated']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    padding: 6px 16px;
}}
QPushButton:hover {{
    background-color: {COLORS['blue']};
    color: #fff;
    border: 1px solid {COLORS['blue']};
}}
QLineEdit, QComboBox, QTableWidget, QTableView {{
    background-color: {COLORS['bg_elevated']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
}}
QHeaderView::section {{
    background-color: {COLORS['bg_card']};
    color: {COLORS['text_secondary']};
    border: 1px solid {COLORS['border']};
    font-weight: 600;
}}
QScrollBar:vertical, QScrollBar:horizontal {{
    background: {COLORS['bg_card']};
    border: none;
    width: 10px;
    margin: 0px;
}}
QScrollBar::handle:vertical, QScrollBar::handle:horizontal {{
    background: {COLORS['blue']};
    min-height: 20px;
    border-radius: 5px;
}}
QScrollBar::add-line, QScrollBar::sub-line {{
    background: none;
    border: none;
}}
QToolTip {{
    background-color: {COLORS['bg_elevated']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
}}
"""

# --- Default Watchlists ---
WATCHLISTS = {
    'tech': ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'META'],
    'finance': ['JPM', 'BAC', 'WFC', 'C', 'GS'],
    'healthcare': ['JNJ', 'PFE', 'MRK', 'ABBV', 'TMO'],
    'energy': ['XOM', 'CVX', 'COP', 'SLB', 'EOG'],
    'custom': [],
}

# --- Placeholder Classes for Data Fetching/Indicators ---
class SimplifiedDataFetcher:
    def fetch_data(self, symbol, period='3mo'):
        import numpy as np
        idx = pd.date_range(end=pd.Timestamp.today(), periods=90)
        df = pd.DataFrame({
            'close': np.random.uniform(100, 200, size=90),
            'sma_20': np.random.uniform(100, 200, size=90),
            'sma_50': np.random.uniform(100, 200, size=90),
            'rsi': np.random.uniform(20, 80, size=90),
            'macd': np.random.uniform(-2, 2, size=90),
            'macd_signal': np.random.uniform(-2, 2, size=90),
        }, index=idx)
        return df
    def fetch_realtime_price(self, symbol):
        return {'price': 150.0, 'change_percent': 0.5}

class AdvancedIndicators:
    @staticmethod
    def calculate_all_indicators(df):
        return df

# --- Required Imports for Charts and Data ---
from PyQt6.QtGui import QBrush, QPainter, QPalette
from PyQt6.QtCore import QMargins
import pandas as pd

# QtCharts for chart widgets
from PyQt6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis, QDateTimeAxis, QBarSet, QBarSeries, QBarCategoryAxis
import os
import sys
import logging
from datetime import datetime
from typing import Dict, List

# Configure logger
logger = logging.getLogger("AlphaFlow")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s')
handler.setFormatter(formatter)
if not logger.hasHandlers():
    logger.addHandler(handler)


# ============================================================================
# DATA WORKER THREAD
# ============================================================================

class DataWorker(QThread):
    """Background worker for fetching market data."""

    data_ready = pyqtSignal(dict)
    error = pyqtSignal(str)
    progress = pyqtSignal(int)

    def __init__(self, symbols: List[str], period: str = "3mo"):
        super().__init__()
        self.symbols = symbols
        self.period = period
        self.fetcher = SimplifiedDataFetcher()

    def run(self):
        """Fetch data for all symbols."""
        results = {}
        total = len(self.symbols)

        for i, symbol in enumerate(self.symbols):
            try:
                data = self.fetcher.fetch_data(symbol, period=self.period)
                if data is not None and len(data) > 0:
                    # Calculate indicators
                    data = AdvancedIndicators.calculate_all_indicators(data)

                    # Get current price info
                    quote = self.fetcher.fetch_realtime_price(symbol)

                    results[symbol] = {
                        'data': data,
                        'quote': quote,
                        'success': True
                    }
                else:
                    results[symbol] = {'success': False, 'error': 'No data'}

            except Exception as e:
                results[symbol] = {'success': False, 'error': str(e)}

            self.progress.emit(int((i + 1) / total * 100))

        self.data_ready.emit(results)


# ============================================================================
# CUSTOM WIDGETS
# ============================================================================

class MetricCard(QFrame):
    """A card displaying a single metric with value and change."""

    def __init__(self, title: str, value: str = "--", change: str = "", icon: str = "", parent=None):
        super().__init__(parent)
        self.setFixedHeight(120)
        self.setMinimumWidth(200)
        card_stylesheet = (
            "QFrame {"
            "background: qlineargradient(x1:0, y1:0, x2:1, y2:1, "
            f"stop:0 {COLORS['bg_card']}, stop:1 {COLORS['bg_elevated']});"
            f"border: 1px solid {COLORS['border']};"
            "border-radius: 16px;"
            "}"
            "QFrame:hover {"
            f"border-color: {COLORS['blue']};"
            "background: qlineargradient(x1:0, y1:0, x2:1, y2:1, "
            f"stop:0 {COLORS['bg_card_hover']}, stop:1 {COLORS['bg_elevated']});"
            "}"
        )
        self.setStyleSheet(card_stylesheet)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(6)

        # Header row with icon and title
        header = QHBoxLayout()
        
        if icon:
            icon_label = QLabel(icon)
            icon_label.setStyleSheet("font-size: 18px;")
            header.addWidget(icon_label)

        # Title
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet(
            f"color: {COLORS['text_secondary']}; font-size: 12px; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px;"
        )
        header.addWidget(self.title_label)
        header.addStretch()
        layout.addLayout(header)

        # Value
        self.value_label = QLabel(value)
        self.value_label.setStyleSheet(
            f"color: {COLORS['text_primary']}; font-size: 28px; font-weight: 700; letter-spacing: -0.5px;"
        )
        layout.addWidget(self.value_label)

        # Change
        self.change_label = QLabel(change)
        self.update_change(change)
        layout.addWidget(self.change_label)
        
        layout.addStretch()

    def update_value(self, value: str):
        self.value_label.setText(value)

    def update_change(self, change: str):
        self.change_label.setText(change)
        if change.startswith('+') or change.startswith('▲'):
            self.change_label.setStyleSheet(
                f"color: {COLORS['green']}; font-size: 13px; font-weight: 600; background: rgba(0, 210, 106, 0.1); padding: 2px 8px; border-radius: 4px;"
            )
        elif change.startswith('-') or change.startswith('▼'):
            self.change_label.setStyleSheet(
                f"color: {COLORS['red']}; font-size: 13px; font-weight: 600; background: rgba(255, 71, 87, 0.1); padding: 2px 8px; border-radius: 4px;"
            )
        else:
            self.change_label.setStyleSheet(
                f"color: {COLORS['text_secondary']}; font-size: 13px;"
            )


class SignalBadge(QLabel):
    """A badge showing buy/sell/hold signal."""

    def __init__(self, signal: str = "HOLD", parent=None):
        super().__init__(signal, parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFixedSize(80, 28)
        self.set_signal(signal)

    def set_signal(self, signal: str):
        self.setText(signal.upper())
        if signal.upper() == "BUY":
            self.setStyleSheet(
                f"background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {COLORS['green']}, stop:1 {COLORS['green_light']}); "
                "color: white; border-radius: 6px; font-weight: 700; font-size: 11px; letter-spacing: 0.5px;"
            )
        elif signal.upper() == "SELL":
            self.setStyleSheet(
                f"background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {COLORS['red']}, stop:1 {COLORS['red_light']}); "
                "color: white; border-radius: 6px; font-weight: 700; font-size: 11px; letter-spacing: 0.5px;"
            )
        else:
            self.setStyleSheet(
                f"background-color: {COLORS['bg_elevated']}; color: {COLORS['text_secondary']}; border: 1px solid {COLORS['border']}; border-radius: 6px; font-weight: 600; font-size: 11px; letter-spacing: 0.5px;"
            )


class StockChart(QChartView):
    """Native stock chart with candlesticks and indicators."""

    def __init__(self, parent=None):
        self.chart = QChart()
        super().__init__(self.chart, parent)

        self.chart.setBackgroundBrush(QBrush(QColor(COLORS['bg_card'])))
        self.chart.setBackgroundRoundness(8)
        self.chart.legend().setVisible(False)
        self.chart.setMargins(QMargins(0, 0, 0, 0))

        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setMinimumHeight(400)

    def update_data(self, df: pd.DataFrame, symbol: str):
        """Update chart with new data."""
        self.chart.removeAllSeries()

        # Remove old axes
        for axis in self.chart.axes():
            self.chart.removeAxis(axis)

        if df is None or len(df) == 0:
            return

        # Create price line series (simplified from candlesticks for performance)
        price_series = QLineSeries()
        price_series.setColor(QColor(COLORS['blue']))

        # SMA lines
        sma20_series = QLineSeries()
        sma20_series.setColor(QColor(COLORS['yellow']))

        sma50_series = QLineSeries()
        sma50_series.setColor(QColor(COLORS['purple']))

        min_price = float('inf')
        max_price = float('-inf')

        for i, (idx, row) in enumerate(df.tail(60).iterrows()):
            _ = idx.timestamp() * 1000 if hasattr(idx, 'timestamp') else i
            close = row.get('close', 0)

            price_series.append(i, close)

            if 'sma_20' in row and pd.notna(row['sma_20']):
                sma20_series.append(i, row['sma_20'])
            if 'sma_50' in row and pd.notna(row['sma_50']):
                sma50_series.append(i, row['sma_50'])

            min_price = min(min_price, close)
            max_price = max(max_price, close)

        self.chart.addSeries(price_series)
        self.chart.addSeries(sma20_series)
        self.chart.addSeries(sma50_series)

        # Create axes
        axis_x = QValueAxis()
        axis_x.setRange(0, 60)
        axis_x.setLabelsVisible(False)
        axis_x.setGridLineColor(QColor(COLORS['border']))
        self.chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)

        padding = (max_price - min_price) * 0.1
        axis_y = QValueAxis()
        axis_y.setRange(min_price - padding, max_price + padding)
        axis_y.setLabelFormat("$%.2f")
        axis_y.setLabelsColor(QColor(COLORS['text_secondary']))
        axis_y.setGridLineColor(QColor(COLORS['border']))
        self.chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)

        price_series.attachAxis(axis_x)
        price_series.attachAxis(axis_y)
        sma20_series.attachAxis(axis_x)
        sma20_series.attachAxis(axis_y)
        sma50_series.attachAxis(axis_x)
        sma50_series.attachAxis(axis_y)

        self.chart.setTitle(f"{symbol} - Price Chart")
        self.chart.setTitleBrush(QBrush(QColor(COLORS['text_primary'])))


class RSIChart(QChartView):
    """RSI indicator chart."""

    def __init__(self, parent=None):
        self.chart = QChart()
        super().__init__(self.chart, parent)

        self.chart.setBackgroundBrush(QBrush(QColor(COLORS['bg_card'])))
        self.chart.legend().setVisible(False)
        self.chart.setMargins(QMargins(0, 0, 0, 0))

        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setFixedHeight(150)

    def update_data(self, df: pd.DataFrame):
        """Update RSI chart."""
        self.chart.removeAllSeries()
        for axis in self.chart.axes():
            self.chart.removeAxis(axis)

        if df is None or 'rsi' not in df.columns:
            return

        rsi_series = QLineSeries()
        rsi_series.setColor(QColor(COLORS['purple']))

        for i, (idx, row) in enumerate(df.tail(60).iterrows()):
            if pd.notna(row.get('rsi')):
                rsi_series.append(i, row['rsi'])

        self.chart.addSeries(rsi_series)

        axis_x = QValueAxis()
        axis_x.setRange(0, 60)
        axis_x.setLabelsVisible(False)
        self.chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)

        axis_y = QValueAxis()
        axis_y.setRange(0, 100)
        axis_y.setLabelsColor(QColor(COLORS['text_secondary']))
        self.chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)

        rsi_series.attachAxis(axis_x)
        rsi_series.attachAxis(axis_y)

        self.chart.setTitle("RSI (14)")
        self.chart.setTitleBrush(QBrush(QColor(COLORS['text_secondary'])))


# ============================================================================
# MAIN PAGES
# ============================================================================

class DashboardPage(QWidget):
    """Main dashboard page."""

    symbol_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.data = {}
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(24, 24, 24, 24)

        # Header
        header = QHBoxLayout()
        header.setSpacing(16)

        # Logo and Title
        title_layout = QVBoxLayout()
        title = QLabel("📈 Dashboard")
        title.setStyleSheet(
            f"font-size: 32px; font-weight: 700; color: {COLORS['text_primary']}; letter-spacing: -0.5px;"
        )
        title_layout.addWidget(title)
        
        subtitle = QLabel("Real-time market analysis and trading signals")
        subtitle.setStyleSheet(
            f"color: {COLORS['text_secondary']}; font-size: 14px;"
        )
        title_layout.addWidget(subtitle)
        
        header.addLayout(title_layout)
        header.addStretch()

        # Market status pill
        self.market_status = QLabel()
        self.market_status.setFixedHeight(32)
        self.update_market_status()
        header.addWidget(self.market_status)

        # Refresh button
        refresh_btn = QPushButton("↻ Refresh")
        refresh_btn.setFixedHeight(36)
        refresh_btn.clicked.connect(self.request_refresh)
        header.addWidget(refresh_btn)

        layout.addLayout(header)

        # Metrics row
        metrics_layout = QHBoxLayout()
        metrics_layout.setSpacing(16)

        self.portfolio_card = MetricCard("Portfolio Value", "$100,000.00", icon="💰")
        self.daily_pnl_card = MetricCard("Daily P&L", "$0.00", icon="📊")
        self.positions_card = MetricCard("Open Positions", "0", icon="📋")
        self.signals_card = MetricCard("Active Signals", "0", icon="🎯")

        metrics_layout.addWidget(self.portfolio_card)
        metrics_layout.addWidget(self.daily_pnl_card)
        metrics_layout.addWidget(self.positions_card)
        metrics_layout.addWidget(self.signals_card)
        metrics_layout.addStretch()

        layout.addLayout(metrics_layout)

        # Main content splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Watchlist table
        watchlist_frame = QFrame()
        watchlist_frame.setStyleSheet(
            f"QFrame {{background-color: {COLORS['bg_card']}; border: 1px solid {COLORS['border']}; border-radius: 16px;}}"
        )
        watchlist_layout = QVBoxLayout(watchlist_frame)
        watchlist_layout.setContentsMargins(20, 20, 20, 20)
        watchlist_layout.setSpacing(16)

        watchlist_header = QHBoxLayout()
        watchlist_title = QLabel("📋 Watchlist")
        watchlist_title.setStyleSheet(
            f"font-size: 18px; font-weight: 600; color: {COLORS['text_primary']};"
        )
        watchlist_header.addWidget(watchlist_title)
        watchlist_header.addStretch()

        self.watchlist_combo = QComboBox()
        self.watchlist_combo.addItems(["Tech", "Finance", "Healthcare", "Energy", "Custom"])
        self.watchlist_combo.currentTextChanged.connect(self.on_watchlist_changed)
        watchlist_header.addWidget(self.watchlist_combo)

        watchlist_layout.addLayout(watchlist_header)

        self.watchlist_table = QTableWidget()
        self.watchlist_table.setColumnCount(6)
        self.watchlist_table.setHorizontalHeaderLabels(["Symbol", "Price", "Change", "RSI", "Trend", "Signal"])
        self.watchlist_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.watchlist_table.setAlternatingRowColors(True)
        self.watchlist_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.watchlist_table.setShowGrid(False)
        self.watchlist_table.verticalHeader().setVisible(False)
        self.watchlist_table.cellClicked.connect(self.on_symbol_clicked)
        watchlist_layout.addWidget(self.watchlist_table)

        splitter.addWidget(watchlist_frame)

        # Chart area
        chart_frame = QFrame()
        chart_frame.setStyleSheet(
            f"QFrame {{background-color: {COLORS['bg_card']}; border: 1px solid {COLORS['border']}; border-radius: 16px;}}"
        )
        chart_layout = QVBoxLayout(chart_frame)
        chart_layout.setContentsMargins(20, 20, 20, 20)
        chart_layout.setSpacing(16)

        self.chart = StockChart()
        chart_layout.addWidget(self.chart)

        self.rsi_chart = RSIChart()
        chart_layout.addWidget(self.rsi_chart)

        splitter.addWidget(chart_frame)
        splitter.setSizes([450, 850])

        layout.addWidget(splitter)

    def update_market_status(self):
        if is_market_open():
            # --- Utility Functions ---
            def is_market_open():
                # Placeholder: always return True for demo
                return True
            self.market_status.setText("  🟢  Market Open  ")
            self.market_status.setStyleSheet(
                f"color: {COLORS['green']}; font-weight: 600; background-color: rgba(0, 210, 106, 0.15); border: 1px solid {COLORS['green']}; border-radius: 16px; padding: 6px 16px; font-size: 13px;"
            )
        else:
            self.market_status.setText("  🔴  Market Closed  ")
            self.market_status.setStyleSheet(
                f"color: {COLORS['red']}; font-weight: 600; background-color: rgba(255, 71, 87, 0.15); border: 1px solid {COLORS['red']}; border-radius: 16px; padding: 6px 16px; font-size: 13px;"
            )

    def request_refresh(self):
        """Request data refresh from main window."""
        self.window().refresh_data()

    def on_watchlist_changed(self, text):
        """Handle watchlist selection change."""
        self.window().change_watchlist(text.lower())

    def on_symbol_clicked(self, row, col):
        """Handle symbol selection."""
        symbol_item = self.watchlist_table.item(row, 0)
        if symbol_item:
            symbol = symbol_item.text()
            self.symbol_selected.emit(symbol)
            self.update_charts(symbol)

    def update_charts(self, symbol: str):
        """Update charts for selected symbol."""
        if symbol in self.data and self.data[symbol].get('success'):
            df = self.data[symbol]['data']
            self.chart.update_data(df, symbol)
            self.rsi_chart.update_data(df)

    def update_data(self, data: Dict):
        """Update dashboard with new data."""
        self.data = data

        # Update watchlist table
        self.watchlist_table.setRowCount(len(data))

        for i, (symbol, info) in enumerate(data.items()):
            if not info.get('success'):
                continue

            df = info.get('data')
            quote = info.get('quote', {})

            # Symbol
            self.watchlist_table.setItem(i, 0, QTableWidgetItem(symbol))

            # Price
            price = quote.get('price', df['close'].iloc[-1] if df is not None else 0)
            price_item = QTableWidgetItem(f"${price:.2f}")
            self.watchlist_table.setItem(i, 1, price_item)

            # Change
            change = quote.get('change_percent', 0)
            change_item = QTableWidgetItem(f"{change:+.2f}%")
            if change > 0:
                change_item.setForeground(QColor(COLORS['green']))
            elif change < 0:
                change_item.setForeground(QColor(COLORS['red']))
            self.watchlist_table.setItem(i, 2, change_item)

            # RSI
            rsi = df['rsi'].iloc[-1] if df is not None and 'rsi' in df else 50
            rsi_item = QTableWidgetItem(f"{rsi:.1f}")
            if rsi > 70:
                rsi_item.setForeground(QColor(COLORS['red']))
            elif rsi < 30:
                rsi_item.setForeground(QColor(COLORS['green']))
            self.watchlist_table.setItem(i, 3, rsi_item)

            # Trend
            if df is not None and 'sma_20' in df and 'sma_50' in df:
                sma20 = df['sma_20'].iloc[-1]
                sma50 = df['sma_50'].iloc[-1]
                if pd.notna(sma20) and pd.notna(sma50):
                    trend = "▲ Up" if sma20 > sma50 else "▼ Down"
                else:
                    trend = "—"
            else:
                trend = "—"
            trend_item = QTableWidgetItem(trend)
            if "Up" in trend:
                trend_item.setForeground(QColor(COLORS['green']))
            elif "Down" in trend:
                trend_item.setForeground(QColor(COLORS['red']))
            self.watchlist_table.setItem(i, 4, trend_item)

            # Signal
            signal = self.calculate_signal(df, rsi)
            signal_item = QTableWidgetItem(signal)
            if signal == "BUY":
                signal_item.setForeground(QColor(COLORS['green']))
            elif signal == "SELL":
                signal_item.setForeground(QColor(COLORS['red']))
            self.watchlist_table.setItem(i, 5, signal_item)

        # Update first symbol chart
        if data:
            first_symbol = list(data.keys())[0]
            self.update_charts(first_symbol)

    def calculate_signal(self, df: pd.DataFrame, rsi: float) -> str:
        """Calculate trading signal based on indicators."""
        if df is None:
            return "HOLD"

        signals = []

        # RSI signals
        if rsi < 30:
            signals.append(1)
        elif rsi > 70:
            signals.append(-1)
        else:
            signals.append(0)

        # MACD signals
        if 'macd' in df and 'macd_signal' in df:
            macd = df['macd'].iloc[-1]
            macd_signal = df['macd_signal'].iloc[-1]
            if pd.notna(macd) and pd.notna(macd_signal):
                if macd > macd_signal:
                    signals.append(1)
                else:
                    signals.append(-1)

        # SMA signals
        if 'sma_20' in df and 'sma_50' in df:
            close = df['close'].iloc[-1]
            sma20 = df['sma_20'].iloc[-1]
            if pd.notna(sma20):
                if close > sma20:
                    signals.append(1)
                else:
                    signals.append(-1)

        avg_signal = sum(signals) / len(signals) if signals else 0

        if avg_signal > 0.3:
            return "BUY"
        elif avg_signal < -0.3:
            return "SELL"
        return "HOLD"


class AnalysisPage(QWidget):
    """Technical analysis page."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.data = {}
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(24, 24, 24, 24)

        # Header
        header = QHBoxLayout()
        header.setSpacing(16)
        
        title_layout = QVBoxLayout()
        title = QLabel("🔍 Technical Analysis")
        title.setStyleSheet(
            f"font-size: 32px; font-weight: 700; color: {COLORS['text_primary']}; letter-spacing: -0.5px;"
        )
        title_layout.addWidget(title)
        
        subtitle = QLabel("Comprehensive indicator analysis")
        subtitle.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 14px;")
        title_layout.addWidget(subtitle)
        
        header.addLayout(title_layout)
        header.addStretch()

        self.symbol_combo = QComboBox()
        self.symbol_combo.setMinimumWidth(180)
        self.symbol_combo.currentTextChanged.connect(self.on_symbol_changed)
        header.addWidget(self.symbol_combo)

        layout.addLayout(header)

        # Analysis content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        content = QWidget()
        content_layout = QVBoxLayout(content)

        # Indicators grid
        indicators_group = QGroupBox("Technical Indicators")
        indicators_layout = QGridLayout(indicators_group)

        self.indicator_labels = {}
        indicators = [
            ("RSI (14)", "rsi"),
            ("MACD", "macd"),
            ("MACD Signal", "macd_signal"),
            ("Stochastic %K", "stoch_k"),
            ("Stochastic %D", "stoch_d"),
            ("ADX", "adx"),
            ("CCI", "cci"),
            ("Williams %R", "williams_r"),
            ("ATR", "atr"),
            ("Momentum", "momentum"),
        ]

        for i, (name, key) in enumerate(indicators):
            row, col = i // 5, (i % 5) * 2
            label = QLabel(f"{name}:")
            label.setStyleSheet(f"color: {COLORS['text_secondary']};")
            indicators_layout.addWidget(label, row, col)

            value = QLabel("--")
            value.setStyleSheet("font-weight: bold;")
            self.indicator_labels[key] = value
            indicators_layout.addWidget(value, row, col + 1)

        content_layout.addWidget(indicators_group)

        # Moving averages
        ma_group = QGroupBox("Moving Averages")
        ma_layout = QGridLayout(ma_group)

        mas = [
            ("SMA 10", "sma_10"),
            ("SMA 20", "sma_20"),
            ("SMA 50", "sma_50"),
            ("SMA 200", "sma_200"),
            ("EMA 12", "ema_12"),
            ("EMA 26", "ema_26"),
        ]

        for i, (name, key) in enumerate(mas):
            row, col = i // 3, (i % 3) * 2
            label = QLabel(f"{name}:")
            label.setStyleSheet(f"color: {COLORS['text_secondary']};")
            ma_layout.addWidget(label, row, col)

            value = QLabel("--")
            value.setStyleSheet("font-weight: bold;")
            self.indicator_labels[key] = value
            ma_layout.addWidget(value, row, col + 1)

        content_layout.addWidget(ma_group)

        # Bollinger Bands
        bb_group = QGroupBox("Bollinger Bands")
        bb_layout = QGridLayout(bb_group)

        bbs = [
            ("Upper Band", "bb_upper"),
            ("Middle Band", "bb_middle"),
            ("Lower Band", "bb_lower"),
            ("Band Width", "bb_width"),
            ("%B", "bb_percent"),
        ]

        for i, (name, key) in enumerate(bbs):
            row, col = i // 3, (i % 3) * 2
            label = QLabel(f"{name}:")
            label.setStyleSheet(f"color: {COLORS['text_secondary']};")
            bb_layout.addWidget(label, row, col)

            value = QLabel("--")
            value.setStyleSheet("font-weight: bold;")
            self.indicator_labels[key] = value
            bb_layout.addWidget(value, row, col + 1)

        content_layout.addWidget(bb_group)

        # Support/Resistance
        sr_group = QGroupBox("Support & Resistance")
        sr_layout = QGridLayout(sr_group)

        levels = [
            ("Pivot", "pivot"),
            ("R1", "r1"),
            ("R2", "r2"),
            ("S1", "s1"),
            ("S2", "s2"),
        ]

        for i, (name, key) in enumerate(levels):
            label = QLabel(f"{name}:")
            label.setStyleSheet(f"color: {COLORS['text_secondary']};")
            sr_layout.addWidget(label, 0, i * 2)

            value = QLabel("--")
            value.setStyleSheet("font-weight: bold;")
            self.indicator_labels[key] = value
            sr_layout.addWidget(value, 0, i * 2 + 1)

        content_layout.addWidget(sr_group)
        content_layout.addStretch()

        scroll.setWidget(content)
        layout.addWidget(scroll)

    def on_symbol_changed(self, symbol):
        """Update analysis for selected symbol."""
        self.update_analysis(symbol)

    def update_data(self, data: Dict):
        """Update available symbols."""
        self.data = data
        current = self.symbol_combo.currentText()
        self.symbol_combo.clear()
        self.symbol_combo.addItems(list(data.keys()))
        if current in data:
            self.symbol_combo.setCurrentText(current)
        elif data:
            self.update_analysis(list(data.keys())[0])

    def update_analysis(self, symbol: str):
        """Update indicator values for symbol."""
        if symbol not in self.data or not self.data[symbol].get('success'):
            return

        df = self.data[symbol]['data']
        if df is None or len(df) == 0:
            return

        latest = df.iloc[-1]

        for key, label in self.indicator_labels.items():
            value = latest.get(key)
            if pd.notna(value):
                if key in ['rsi', 'stoch_k', 'stoch_d', 'adx', 'williams_r', 'bb_percent']:
                    label.setText(f"{value:.1f}")
                elif key in ['macd', 'macd_signal', 'momentum', 'cci']:
                    label.setText(f"{value:.2f}")
                elif key in ['bb_width']:
                    label.setText(f"{value:.3f}")
                else:
                    label.setText(f"${value:.2f}")
            else:
                label.setText("--")


# ============================================================================
# PORTFOLIO PAGE
# ============================================================================

class PortfolioPage(QWidget):
    """Portfolio management page."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(24, 24, 24, 24)

        # Header
        header = QHBoxLayout()
        title_layout = QVBoxLayout()
        title = QLabel("💼 Portfolio")
        title.setStyleSheet(
            f"font-size: 32px; font-weight: 700; color: {COLORS['text_primary']};"
        )
        title_layout.addWidget(title)
        subtitle = QLabel("Track your positions and performance")
        subtitle.setStyleSheet(
            f"color: {COLORS['text_secondary']}; font-size: 14px;"
        )
        title_layout.addWidget(subtitle)
        header.addLayout(title_layout)
        header.addStretch()
        layout.addLayout(header)

        # Portfolio summary cards
        summary_layout = QHBoxLayout()
        summary_layout.setSpacing(16)

        self.total_value_card = MetricCard("Total Value", "$100,000.00", icon="💰")
        self.total_pnl_card = MetricCard("Total P&L", "$0.00", "+0.00%", icon="📈")
        self.cash_card = MetricCard("Available Cash", "$100,000.00", icon="💵")
        self.buying_power_card = MetricCard("Buying Power", "$400,000.00", icon="⚡")

        summary_layout.addWidget(self.total_value_card)
        summary_layout.addWidget(self.total_pnl_card)
        summary_layout.addWidget(self.cash_card)
        summary_layout.addWidget(self.buying_power_card)
        summary_layout.addStretch()
        layout.addLayout(summary_layout)

        # Positions table
        positions_frame = QFrame()
        positions_frame.setStyleSheet(
            f"QFrame {{background-color: {COLORS['bg_card']}; border: 1px solid {COLORS['border']}; border-radius: 16px;}}"
        )
        positions_layout = QVBoxLayout(positions_frame)
        positions_layout.setContentsMargins(20, 20, 20, 20)

        positions_header = QLabel("📋 Open Positions")
        positions_header.setStyleSheet(f"font-size: 18px; font-weight: 600; color: {COLORS['text_primary']};")
        positions_layout.addWidget(positions_header)

        self.positions_table = QTableWidget()
        self.positions_table.setColumnCount(8)
        self.positions_table.setHorizontalHeaderLabels([
            "Symbol", "Qty", "Avg Cost", "Current", "Market Value", "P&L", "P&L %", "Action"
        ])
        self.positions_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.positions_table.setAlternatingRowColors(True)
        self.positions_table.setShowGrid(False)
        self.positions_table.verticalHeader().setVisible(False)
        positions_layout.addWidget(self.positions_table)

        layout.addWidget(positions_frame)

        # Trade history
        history_frame = QFrame()
        history_frame.setStyleSheet(
            f"QFrame {{background-color: {COLORS['bg_card']}; border: 1px solid {COLORS['border']}; border-radius: 16px;}}"
        )
        history_layout = QVBoxLayout(history_frame)
        history_layout.setContentsMargins(20, 20, 20, 20)

        history_header = QLabel("📜 Trade History")
        history_header.setStyleSheet(f"font-size: 18px; font-weight: 600; color: {COLORS['text_primary']};")
        history_layout.addWidget(history_header)

        self.history_table = QTableWidget()
        self.history_table.setColumnCount(7)
        self.history_table.setHorizontalHeaderLabels([
            "Date", "Symbol", "Side", "Qty", "Price", "Total", "Status"
        ])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.history_table.setAlternatingRowColors(True)
        self.history_table.setShowGrid(False)
        self.history_table.verticalHeader().setVisible(False)
        history_layout.addWidget(self.history_table)

        layout.addWidget(history_frame)


# ============================================================================
# BACKTEST PAGE
# ============================================================================

class BacktestPage(QWidget):
    """Backtesting page."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(24, 24, 24, 24)

        # Header
        header = QHBoxLayout()
        title_layout = QVBoxLayout()
        title = QLabel("🧪 Backtesting")
        title.setStyleSheet(
            f"font-size: 32px; font-weight: 700; color: {COLORS['text_primary']};"
        )
        title_layout.addWidget(title)
        subtitle = QLabel("Test strategies on historical data")
        subtitle.setStyleSheet(
            f"color: {COLORS['text_secondary']}; font-size: 14px;"
        )
        title_layout.addWidget(subtitle)
        header.addLayout(title_layout)
        header.addStretch()

        run_btn = QPushButton("▶️  Run Backtest")
        run_btn.setFixedHeight(40)
        run_btn.clicked.connect(self.run_backtest)
        header.addWidget(run_btn)

        layout.addLayout(header)

        # Configuration
        config_frame = QFrame()
        config_frame.setStyleSheet(
            f"QFrame {{background-color: {COLORS['bg_card']}; border: 1px solid {COLORS['border']}; border-radius: 16px;}}"
        )
        config_layout = QHBoxLayout(config_frame)
        config_layout.setContentsMargins(20, 20, 20, 20)
        config_layout.setSpacing(24)

        # Symbol
        symbol_layout = QVBoxLayout()
        symbol_label = QLabel("Symbol")
        symbol_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
        symbol_layout.addWidget(symbol_label)
        self.symbol_input = QComboBox()
        self.symbol_input.addItems(['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN', 'META', 'NVDA'])
        self.symbol_input.setEditable(True)
        symbol_layout.addWidget(self.symbol_input)
        config_layout.addLayout(symbol_layout)

        # Strategy
        strategy_layout = QVBoxLayout()
        strategy_label = QLabel("Strategy")
        strategy_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
        strategy_layout.addWidget(strategy_label)
        self.strategy_combo = QComboBox()
        self.strategy_combo.addItems([
            'RSI Mean Reversion', 'MACD Crossover', 'Moving Average Crossover',
            'Bollinger Bands', 'Trend Following', 'ML Prediction'
        ])
        strategy_layout.addWidget(self.strategy_combo)
        config_layout.addLayout(strategy_layout)

        # Period
        period_layout = QVBoxLayout()
        period_label = QLabel("Period")
        period_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
        period_layout.addWidget(period_label)
        self.period_combo = QComboBox()
        self.period_combo.addItems(['1 Month', '3 Months', '6 Months', '1 Year', '2 Years', '5 Years'])
        self.period_combo.setCurrentIndex(2)
        period_layout.addWidget(self.period_combo)
        config_layout.addLayout(period_layout)

        # Initial Capital
        capital_layout = QVBoxLayout()
        capital_label = QLabel("Initial Capital")
        capital_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
        capital_layout.addWidget(capital_label)
        self.capital_input = QDoubleSpinBox()
        self.capital_input.setRange(1000, 10000000)
        self.capital_input.setValue(100000)
        self.capital_input.setPrefix("$")
        capital_layout.addWidget(self.capital_input)
        config_layout.addLayout(capital_layout)

        config_layout.addStretch()
        layout.addWidget(config_frame)

        # Results
        results_layout = QHBoxLayout()
        results_layout.setSpacing(16)

        # Metrics
        metrics_frame = QFrame()
        metrics_frame.setStyleSheet(
            f"QFrame {{background-color: {COLORS['bg_card']}; border: 1px solid {COLORS['border']}; border-radius: 16px;}}"
        )
        metrics_layout = QVBoxLayout(metrics_frame)
        metrics_layout.setContentsMargins(20, 20, 20, 20)

        metrics_title = QLabel("📊 Performance Metrics")
        metrics_title.setStyleSheet(f"font-size: 18px; font-weight: 600; color: {COLORS['text_primary']};")
        metrics_layout.addWidget(metrics_title)

        self.metrics_labels = {}
        metrics = [
            ("Total Return", "total_return"),
            ("Sharpe Ratio", "sharpe"),
            ("Max Drawdown", "max_dd"),
            ("Win Rate", "win_rate"),
            ("Total Trades", "total_trades"),
            ("Profit Factor", "profit_factor"),
            ("Avg Win", "avg_win"),
            ("Avg Loss", "avg_loss"),
        ]

        metrics_grid = QGridLayout()
        for i, (name, key) in enumerate(metrics):
            row, col = i // 2, (i % 2) * 2
            label = QLabel(f"{name}:")
            label.setStyleSheet(f"color: {COLORS['text_secondary']};")
            metrics_grid.addWidget(label, row, col)
            value = QLabel("--")
            value.setStyleSheet("font-weight: 600;")
            self.metrics_labels[key] = value
            metrics_grid.addWidget(value, row, col + 1)

        metrics_layout.addLayout(metrics_grid)
        metrics_layout.addStretch()
        results_layout.addWidget(metrics_frame)

        # Equity curve placeholder
        chart_frame = QFrame()
        chart_frame.setStyleSheet(
            f"QFrame {{background-color: {COLORS['bg_card']}; border: 1px solid {COLORS['border']}; border-radius: 16px;}}"
        )
        chart_layout = QVBoxLayout(chart_frame)
        chart_layout.setContentsMargins(20, 20, 20, 20)

        chart_title = QLabel("📈 Equity Curve")
        chart_title.setStyleSheet(f"font-size: 18px; font-weight: 600; color: {COLORS['text_primary']};")
        chart_layout.addWidget(chart_title)

        self.equity_chart = StockChart()
        chart_layout.addWidget(self.equity_chart)

        results_layout.addWidget(chart_frame, 2)
        layout.addLayout(results_layout)

    def run_backtest(self):
        """Run the backtest."""
        # This would connect to the core backtester
        QMessageBox.information(self, "Backtest", "Backtest started! Results will appear shortly.")


# ============================================================================
# TRADING PAGE
# ============================================================================

class TradingPage(QWidget):
    """Order execution and trading page."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(24, 24, 24, 24)

        # Header
        header = QHBoxLayout()
        title_layout = QVBoxLayout()
        title = QLabel("💹 Trading")
        title.setStyleSheet(
            f"font-size: 32px; font-weight: 700; color: {COLORS['text_primary']};"
        )
        title_layout.addWidget(title)
        subtitle = QLabel("Execute trades and manage orders")
        subtitle.setStyleSheet(
            f"color: {COLORS['text_secondary']}; font-size: 14px;"
        )
        title_layout.addWidget(subtitle)
        header.addLayout(title_layout)
        header.addStretch()
        layout.addLayout(header)

        # Main content
        content = QHBoxLayout()
        content.setSpacing(20)

        # Order entry panel
        order_frame = QFrame()
        order_frame.setFixedWidth(400)
        order_frame.setStyleSheet(
            f"QFrame {{background-color: {COLORS['bg_card']}; border: 1px solid {COLORS['border']}; border-radius: 16px;}}"
        )
        order_layout = QVBoxLayout(order_frame)
        order_layout.setContentsMargins(24, 24, 24, 24)
        order_layout.setSpacing(16)

        order_title = QLabel("📝 New Order")
        order_title.setStyleSheet(f"font-size: 18px; font-weight: 600; color: {COLORS['text_primary']};")
        order_layout.addWidget(order_title)

        # Symbol
        self.order_symbol = QLineEdit()
        self.order_symbol.setPlaceholderText("Symbol (e.g., AAPL)")
        order_layout.addWidget(self.order_symbol)

        # Side buttons
        side_layout = QHBoxLayout()
        self.buy_btn = QPushButton("BUY")
        self.buy_btn.setCheckable(True)
        self.buy_btn.setStyleSheet(
            f"QPushButton {{background: {COLORS['green']}; color: white; font-weight: 700; padding: 12px; border-radius: 8px;}} "
            f"QPushButton:checked {{background: {COLORS['green']}; border: 2px solid white;}}"
        )
        side_layout.addWidget(self.buy_btn)

        self.sell_btn = QPushButton("SELL")
        self.sell_btn.setCheckable(True)
        self.sell_btn.setStyleSheet(
            f"QPushButton {{background: {COLORS['red']}; color: white; font-weight: 700; padding: 12px; border-radius: 8px;}} "
            f"QPushButton:checked {{background: {COLORS['red']}; border: 2px solid white;}}"
        )
        side_layout.addWidget(self.sell_btn)
        order_layout.addLayout(side_layout)

        # Order type
        type_label = QLabel("Order Type")
        type_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        order_layout.addWidget(type_label)
        self.order_type = QComboBox()
        self.order_type.addItems(['Market', 'Limit', 'Stop', 'Stop Limit'])
        order_layout.addWidget(self.order_type)

        # Quantity
        qty_label = QLabel("Quantity")
        qty_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        order_layout.addWidget(qty_label)
        self.order_qty = QSpinBox()
        self.order_qty.setRange(1, 100000)
        self.order_qty.setValue(100)
        order_layout.addWidget(self.order_qty)

        # Price (for limit orders)
        price_label = QLabel("Limit Price")
        price_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        order_layout.addWidget(price_label)
        self.order_price = QDoubleSpinBox()
        self.order_price.setRange(0.01, 100000)
        self.order_price.setPrefix("$")
        order_layout.addWidget(self.order_price)

        # Time in force
        tif_label = QLabel("Time in Force")
        tif_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        order_layout.addWidget(tif_label)
        self.time_in_force = QComboBox()
        self.time_in_force.addItems(['Day', 'GTC', 'IOC', 'FOK'])
        order_layout.addWidget(self.time_in_force)

        order_layout.addStretch()

        # Submit button
        submit_btn = QPushButton("📤  Submit Order")
        submit_btn.setFixedHeight(44)
        submit_btn.clicked.connect(self.submit_order)
        order_layout.addWidget(submit_btn)

        content.addWidget(order_frame)

        # Orders panel
        orders_frame = QFrame()
        orders_frame.setStyleSheet(
            f"QFrame {{background-color: {COLORS['bg_card']}; border: 1px solid {COLORS['border']}; border-radius: 16px;}}"
        )
        orders_layout = QVBoxLayout(orders_frame)
        orders_layout.setContentsMargins(20, 20, 20, 20)

        orders_title = QLabel("📋 Open Orders")
        orders_title.setStyleSheet(f"font-size: 18px; font-weight: 600; color: {COLORS['text_primary']};")
        orders_layout.addWidget(orders_title)

        self.orders_table = QTableWidget()
        self.orders_table.setColumnCount(7)
        self.orders_table.setHorizontalHeaderLabels([
            "Time", "Symbol", "Side", "Type", "Qty", "Price", "Status"
        ])
        self.orders_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.orders_table.setAlternatingRowColors(True)
        self.orders_table.setShowGrid(False)
        self.orders_table.verticalHeader().setVisible(False)
        orders_layout.addWidget(self.orders_table)

        content.addWidget(orders_frame)
        layout.addLayout(content)

    def submit_order(self):
        """Submit the order."""
        symbol = self.order_symbol.text().upper()
        if not symbol:
            QMessageBox.warning(self, "Error", "Please enter a symbol")
            return
        side = "BUY" if self.buy_btn.isChecked() else "SELL"
        qty = self.order_qty.value()
        QMessageBox.information(self, "Order Submitted", f"{side} {qty} shares of {symbol}")


# ============================================================================
# ALERTS PAGE
# ============================================================================

class AlertsPage(QWidget):
    """Price alerts and notifications page."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.alerts = []
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(24, 24, 24, 24)

        # Header
        header = QHBoxLayout()
        title_layout = QVBoxLayout()
        title = QLabel("🔔 Alerts")
        title.setStyleSheet(
            f"font-size: 32px; font-weight: 700; color: {COLORS['text_primary']};"
        )
        title_layout.addWidget(title)
        subtitle = QLabel("Set price alerts and notifications")
        subtitle.setStyleSheet(
            f"color: {COLORS['text_secondary']}; font-size: 14px;"
        )
        title_layout.addWidget(subtitle)
        header.addLayout(title_layout)
        header.addStretch()
        layout.addLayout(header)

        # Create alert form
        form_frame = QFrame()
        form_frame.setStyleSheet(
            f"QFrame {{background-color: {COLORS['bg_card']}; border: 1px solid {COLORS['border']}; border-radius: 16px;}}"
        )
        form_layout = QHBoxLayout(form_frame)
        form_layout.setContentsMargins(20, 20, 20, 20)
        form_layout.setSpacing(16)

        # Symbol
        symbol_layout = QVBoxLayout()
        symbol_label = QLabel("Symbol")
        symbol_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
        symbol_layout.addWidget(symbol_label)
        self.alert_symbol = QLineEdit()
        self.alert_symbol.setPlaceholderText("AAPL")
        symbol_layout.addWidget(self.alert_symbol)
        form_layout.addLayout(symbol_layout)

        # Condition
        condition_layout = QVBoxLayout()
        condition_label = QLabel("Condition")
        condition_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
        condition_layout.addWidget(condition_label)
        self.alert_condition = QComboBox()
        self.alert_condition.addItems([
            'Price Above', 'Price Below', 'RSI Above', 'RSI Below',
            'MACD Crossover', 'Volume Spike', 'Price Change %'
        ])
        condition_layout.addWidget(self.alert_condition)
        form_layout.addLayout(condition_layout)

        # Value
        value_layout = QVBoxLayout()
        value_label = QLabel("Value")
        value_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
        value_layout.addWidget(value_label)
        self.alert_value = QDoubleSpinBox()
        self.alert_value.setRange(0, 100000)
        value_layout.addWidget(self.alert_value)
        form_layout.addLayout(value_layout)

        # Add button
        add_btn = QPushButton("➕ Add Alert")
        add_btn.setFixedHeight(38)
        add_btn.clicked.connect(self.add_alert)
        form_layout.addWidget(add_btn, alignment=Qt.AlignmentFlag.AlignBottom)

        form_layout.addStretch()
        layout.addWidget(form_frame)

        # Alerts table
        alerts_frame = QFrame()
        alerts_frame.setStyleSheet(
            f"QFrame {{background-color: {COLORS['bg_card']}; border: 1px solid {COLORS['border']}; border-radius: 16px;}}"
        )
        alerts_layout = QVBoxLayout(alerts_frame)
        alerts_layout.setContentsMargins(20, 20, 20, 20)

        alerts_header = QLabel("📋 Active Alerts")
        alerts_header.setStyleSheet(f"font-size: 18px; font-weight: 600; color: {COLORS['text_primary']};")
        alerts_layout.addWidget(alerts_header)

        self.alerts_table = QTableWidget()
        self.alerts_table.setColumnCount(5)
        self.alerts_table.setHorizontalHeaderLabels(["Symbol", "Condition", "Value", "Status", "Action"])
        self.alerts_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.alerts_table.setAlternatingRowColors(True)
        self.alerts_table.setShowGrid(False)
        self.alerts_table.verticalHeader().setVisible(False)
        alerts_layout.addWidget(self.alerts_table)

        layout.addWidget(alerts_frame)

    def add_alert(self):
        """Add a new alert."""
        symbol = self.alert_symbol.text().upper()
        if not symbol:
            return
        condition = self.alert_condition.currentText()
        value = self.alert_value.value()

        row = self.alerts_table.rowCount()
        self.alerts_table.insertRow(row)
        self.alerts_table.setItem(row, 0, QTableWidgetItem(symbol))
        self.alerts_table.setItem(row, 1, QTableWidgetItem(condition))
        self.alerts_table.setItem(row, 2, QTableWidgetItem(str(value)))
        
        status = QTableWidgetItem("Active")
        status.setForeground(QColor(COLORS['green']))
        self.alerts_table.setItem(row, 3, status)

        delete_btn = QPushButton("🗑️")
        delete_btn.clicked.connect(lambda: self.alerts_table.removeRow(row))
        self.alerts_table.setCellWidget(row, 4, delete_btn)


# ============================================================================
# RISK MANAGEMENT PAGE
# ============================================================================

class RiskPage(QWidget):
    """Risk management and analytics page."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(24, 24, 24, 24)

        # Header
        header = QHBoxLayout()
        title_layout = QVBoxLayout()
        title = QLabel("⚠️ Risk Management")
        title.setStyleSheet(
            f"font-size: 32px; font-weight: 700; color: {COLORS['text_primary']};"
        )
        title_layout.addWidget(title)
        subtitle = QLabel("Monitor and control trading risk")
        subtitle.setStyleSheet(
            f"color: {COLORS['text_secondary']}; font-size: 14px;"
        )
        title_layout.addWidget(subtitle)
        header.addLayout(title_layout)
        header.addStretch()
        layout.addLayout(header)

        # Risk metrics
        metrics_layout = QHBoxLayout()
        metrics_layout.setSpacing(16)

        self.var_card = MetricCard("Value at Risk (95%)", "$0.00", icon="📉")
        self.max_dd_card = MetricCard("Max Drawdown", "0.00%", icon="📊")
        self.beta_card = MetricCard("Portfolio Beta", "0.00", icon="📈")
        self.sharpe_card = MetricCard("Sharpe Ratio", "0.00", icon="⭐")

        metrics_layout.addWidget(self.var_card)
        metrics_layout.addWidget(self.max_dd_card)
        metrics_layout.addWidget(self.beta_card)
        metrics_layout.addWidget(self.sharpe_card)
        metrics_layout.addStretch()
        layout.addLayout(metrics_layout)

        # Main content
        content = QHBoxLayout()
        content.setSpacing(20)

        # Risk settings
        settings_frame = QFrame()
        settings_frame.setStyleSheet(
            f"QFrame {{background-color: {COLORS['bg_card']}; border: 1px solid {COLORS['border']}; border-radius: 16px;}}"
        )
        settings_layout = QVBoxLayout(settings_frame)
        settings_layout.setContentsMargins(20, 20, 20, 20)

        settings_title = QLabel("⚙️ Risk Settings")
        settings_title.setStyleSheet(f"font-size: 18px; font-weight: 600; color: {COLORS['text_primary']};")
        settings_layout.addWidget(settings_title)

        form = QFormLayout()
        form.setSpacing(12)

        self.max_position_size = QDoubleSpinBox()
        self.max_position_size.setRange(1, 100)
        self.max_position_size.setValue(10)
        self.max_position_size.setSuffix("%")
        form.addRow("Max Position Size:", self.max_position_size)

        self.max_daily_loss = QDoubleSpinBox()
        self.max_daily_loss.setRange(0.5, 20)
        self.max_daily_loss.setValue(2)
        self.max_daily_loss.setSuffix("%")
        form.addRow("Max Daily Loss:", self.max_daily_loss)

        self.max_drawdown = QDoubleSpinBox()
        self.max_drawdown.setRange(5, 50)
        self.max_drawdown.setValue(15)
        self.max_drawdown.setSuffix("%")
        form.addRow("Max Drawdown:", self.max_drawdown)

        self.stop_loss_default = QDoubleSpinBox()
        self.stop_loss_default.setRange(0.5, 20)
        self.stop_loss_default.setValue(2)
        self.stop_loss_default.setSuffix("%")
        form.addRow("Default Stop Loss:", self.stop_loss_default)

        self.take_profit_default = QDoubleSpinBox()
        self.take_profit_default.setRange(1, 100)
        self.take_profit_default.setValue(5)
        self.take_profit_default.setSuffix("%")
        form.addRow("Default Take Profit:", self.take_profit_default)

        settings_layout.addLayout(form)
        settings_layout.addStretch()

        save_btn = QPushButton("💾 Save Settings")
        save_btn.clicked.connect(lambda: QMessageBox.information(self, "Saved", "Risk settings saved!"))
        settings_layout.addWidget(save_btn)

        content.addWidget(settings_frame)

        # Position sizing calculator
        calc_frame = QFrame()
        calc_frame.setStyleSheet(
            f"QFrame {{background-color: {COLORS['bg_card']}; border: 1px solid {COLORS['border']}; border-radius: 16px;}}"
        )
        calc_layout = QVBoxLayout(calc_frame)
        calc_layout.setContentsMargins(20, 20, 20, 20)

        calc_title = QLabel("🧮 Position Size Calculator")
        calc_title.setStyleSheet(f"font-size: 18px; font-weight: 600; color: {COLORS['text_primary']};")
        calc_layout.addWidget(calc_title)

        calc_form = QFormLayout()
        calc_form.setSpacing(12)

        self.calc_capital = QDoubleSpinBox()
        self.calc_capital.setRange(1000, 10000000)
        self.calc_capital.setValue(100000)
        self.calc_capital.setPrefix("$")
        calc_form.addRow("Account Size:", self.calc_capital)

        self.calc_risk = QDoubleSpinBox()
        self.calc_risk.setRange(0.1, 10)
        self.calc_risk.setValue(1)
        self.calc_risk.setSuffix("%")
        calc_form.addRow("Risk per Trade:", self.calc_risk)

        self.calc_entry = QDoubleSpinBox()
        self.calc_entry.setRange(0.01, 10000)
        self.calc_entry.setValue(150)
        self.calc_entry.setPrefix("$")
        calc_form.addRow("Entry Price:", self.calc_entry)

        self.calc_stop = QDoubleSpinBox()
        self.calc_stop.setRange(0.01, 10000)
        self.calc_stop.setValue(145)
        self.calc_stop.setPrefix("$")
        calc_form.addRow("Stop Loss Price:", self.calc_stop)

        calc_layout.addLayout(calc_form)

        calc_btn = QPushButton("Calculate")
        calc_btn.clicked.connect(self.calculate_position)
        calc_layout.addWidget(calc_btn)

        self.calc_result = QLabel("Position Size: -- shares")
        self.calc_result.setStyleSheet(
            f"font-size: 18px; font-weight: 600; color: {COLORS['blue_light']}; padding: 16px; background-color: {COLORS['bg_elevated']}; border-radius: 8px;"
        )
        self.calc_result.setAlignment(Qt.AlignmentFlag.AlignCenter)
        calc_layout.addWidget(self.calc_result)

        calc_layout.addStretch()
        content.addWidget(calc_frame)

        layout.addLayout(content)

    def calculate_position(self):
        """Calculate position size."""
        capital = self.calc_capital.value()
        risk_pct = self.calc_risk.value() / 100
        entry = self.calc_entry.value()
        stop = self.calc_stop.value()

        risk_amount = capital * risk_pct
        price_diff = abs(entry - stop)

        if price_diff > 0:
            shares = int(risk_amount / price_diff)
            self.calc_result.setText(f"Position Size: {shares:,} shares\n(Risk: ${risk_amount:,.2f})")
        else:
            self.calc_result.setText("Invalid stop loss")


class SettingsPage(QWidget):
    """Settings page."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = QSettings("AlphaFlow", "TradingApp")
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(24)
        layout.setContentsMargins(24, 24, 24, 24)

        # Header
        title_layout = QVBoxLayout()
        title = QLabel("⚙️ Settings")
        title.setStyleSheet(
            f"font-size: 32px; font-weight: 700; color: {COLORS['text_primary']}; letter-spacing: -0.5px;"
        )
        title_layout.addWidget(title)
        
        subtitle = QLabel("Configure your trading preferences")
        subtitle.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 14px;")
        title_layout.addWidget(subtitle)
        
        layout.addLayout(title_layout)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        content = QWidget()
        content_layout = QVBoxLayout(content)

        # API Settings
        api_group = QGroupBox("API Configuration")
        api_layout = QFormLayout(api_group)

        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("Enter Alpaca API Key")
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        api_layout.addRow("API Key:", self.api_key_input)

        self.secret_key_input = QLineEdit()
        self.secret_key_input.setPlaceholderText("Enter Alpaca Secret Key")
        self.secret_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        api_layout.addRow("Secret Key:", self.secret_key_input)

        self.paper_trading_check = QCheckBox("Paper Trading (Sandbox)")
        self.paper_trading_check.setChecked(True)
        api_layout.addRow("", self.paper_trading_check)

        content_layout.addWidget(api_group)

        # Trading Settings
        trading_group = QGroupBox("Trading Settings")
        trading_layout = QFormLayout(trading_group)

        self.initial_capital = QDoubleSpinBox()
        self.initial_capital.setRange(1000, 10000000)
        self.initial_capital.setValue(100000)
        self.initial_capital.setPrefix("$")
        trading_layout.addRow("Initial Capital:", self.initial_capital)

        self.max_position = QDoubleSpinBox()
        self.max_position.setRange(1, 100)
        self.max_position.setValue(10)
        self.max_position.setSuffix("%")
        trading_layout.addRow("Max Position Size:", self.max_position)

        self.stop_loss = QDoubleSpinBox()
        self.stop_loss.setRange(0.5, 20)
        self.stop_loss.setValue(2)
        self.stop_loss.setSuffix("%")
        trading_layout.addRow("Default Stop Loss:", self.stop_loss)

        content_layout.addWidget(trading_group)

        # Display Settings
        display_group = QGroupBox("Display Settings")
        display_layout = QFormLayout(display_group)

        self.auto_refresh_check = QCheckBox("Auto-refresh data")
        display_layout.addRow("", self.auto_refresh_check)

        self.refresh_interval = QSpinBox()
        self.refresh_interval.setRange(30, 300)
        self.refresh_interval.setValue(60)
        self.refresh_interval.setSuffix(" seconds")
        display_layout.addRow("Refresh Interval:", self.refresh_interval)

        content_layout.addWidget(display_group)

        # Save button
        save_btn = QPushButton("💾 Save Settings")
        save_btn.clicked.connect(self.save_settings)
        content_layout.addWidget(save_btn)

        content_layout.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll)

    def load_settings(self):
        """Load saved settings."""
        self.api_key_input.setText(self.settings.value("api_key", ""))
        self.secret_key_input.setText(self.settings.value("secret_key", ""))
        self.paper_trading_check.setChecked(self.settings.value("paper_trading", True, type=bool))
        self.initial_capital.setValue(self.settings.value("initial_capital", 100000, type=float))
        self.max_position.setValue(self.settings.value("max_position", 10, type=float))
        self.stop_loss.setValue(self.settings.value("stop_loss", 2, type=float))
        self.auto_refresh_check.setChecked(self.settings.value("auto_refresh", False, type=bool))
        self.refresh_interval.setValue(self.settings.value("refresh_interval", 60, type=int))

    def save_settings(self):
        """Save settings."""
        self.settings.setValue("api_key", self.api_key_input.text())
        self.settings.setValue("secret_key", self.secret_key_input.text())
        self.settings.setValue("paper_trading", self.paper_trading_check.isChecked())
        self.settings.setValue("initial_capital", self.initial_capital.value())
        self.settings.setValue("max_position", self.max_position.value())
        self.settings.setValue("stop_loss", self.stop_loss.value())
        self.settings.setValue("auto_refresh", self.auto_refresh_check.isChecked())
        self.settings.setValue("refresh_interval", self.refresh_interval.value())

        QMessageBox.information(self, "Settings Saved", "Your settings have been saved successfully.")


class AboutPage(QWidget):
    """About page."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(24)
        layout.setContentsMargins(60, 60, 60, 60)

        # Logo/Icon with glow effect
        logo = QLabel("📈")
        logo.setStyleSheet("font-size: 80px;")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo)

        # Title with gradient-like effect
        title = QLabel("AlphaFlow")
        title.setStyleSheet(
            f"font-size: 42px; font-weight: 800; color: {COLORS['blue_light']}; letter-spacing: -1px;"
        )
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Version badge
        version = QLabel("Version 1.0.0")
        version.setStyleSheet(
            f"font-size: 14px; color: {COLORS['text_secondary']}; background-color: {COLORS['bg_elevated']}; padding: 6px 16px; border-radius: 12px;"
        )
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version.setFixedWidth(140)
        
        version_container = QHBoxLayout()
        version_container.addStretch()
        version_container.addWidget(version)
        version_container.addStretch()
        layout.addLayout(version_container)

        # Description
        desc = QLabel("Professional Algorithmic Trading Platform")
        desc.setStyleSheet(
            f"font-size: 18px; color: {COLORS['text_primary']}; font-weight: 500;"
        )
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc)

        layout.addSpacing(20)

        # Features grid
        features_frame = QFrame()
        features_frame.setStyleSheet(
            f"QFrame {{background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {COLORS['bg_card']}, stop:1 {COLORS['bg_elevated']}); border: 1px solid {COLORS['border']}; border-radius: 20px;}}"
        )
        features_frame.setMaximumWidth(500)
        features_layout = QGridLayout(features_frame)
        features_layout.setContentsMargins(32, 24, 32, 24)
        features_layout.setSpacing(16)

        features = [
            ("📊", "Real-time Market Data"),
            ("🧠", "ML Predictions"),
            ("📈", "20+ Indicators"),
            ("💼", "Portfolio Tracking"),
            ("⚠️", "Risk Analytics"),
            ("📉", "Options Pricing"),
        ]

        for i, (icon, text) in enumerate(features):
            row, col = i // 2, i % 2
            
            feature_widget = QWidget()
            feature_layout = QHBoxLayout(feature_widget)
            feature_layout.setContentsMargins(0, 0, 0, 0)
            feature_layout.setSpacing(12)
            
            icon_label = QLabel(icon)
            icon_label.setStyleSheet("font-size: 20px;")
            feature_layout.addWidget(icon_label)
            
            text_label = QLabel(text)
            text_label.setStyleSheet(
                f"font-size: 14px; font-weight: 500; color: {COLORS['text_primary']};"
            )
            feature_layout.addWidget(text_label)
            feature_layout.addStretch()
            
            features_layout.addWidget(feature_widget, row, col)

        features_container = QHBoxLayout()
        features_container.addStretch()
        features_container.addWidget(features_frame)
        features_container.addStretch()
        layout.addLayout(features_container)

        layout.addStretch()

        # Copyright
        copyright_label = QLabel("© 2024-2026 The Align Project")
        copyright_label.setStyleSheet(
            f"font-size: 13px; color: {COLORS.get('text_muted', COLORS['text_secondary'])};"
        )
        copyright_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(copyright_label)


# ============================================================================
# MAIN WINDOW
# ============================================================================

class AlphaFlowWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.data = {}
        self.current_watchlist = WATCHLISTS.get('tech', ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'META'])
        self.worker = None
        self.setup_ui()
        self.create_menu_bar()
        self.create_status_bar()

        # Auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_data)

        # Initial data load
        QTimer.singleShot(500, self.refresh_data)

    def setup_ui(self):
        """Setup the main UI with a modern sidebar navigation."""
        self.setWindowTitle("AlphaFlow - Algorithmic Trading Platform")
        self.setMinimumSize(1400, 900)

        # Center on screen
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(
            (screen.width() - 1400) // 2,
            (screen.height() - 900) // 2,
            1400, 900
        )

        # Central widget with sidebar and content
        central = QWidget()
        central.setStyleSheet(f"background-color: {COLORS['bg_dark']};")
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(210)
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setStyleSheet(
            f"QFrame#sidebar {{background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {COLORS['gradient_start']}, stop:1 {COLORS['gradient_end']}); border: none; border-top-right-radius: 24px; border-bottom-right-radius: 24px; box-shadow: 0 0 32px 0 #0008;}}"
        )
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 32, 0, 32)
        sidebar_layout.setSpacing(8)

        # Sidebar buttons (icon, label)
        self.sidebar_buttons = []
        sidebar_items = [
            ("📈", "Dashboard"),
            ("🔍", "Analysis"),
            ("💼", "Portfolio"),
            ("🧪", "Backtest"),
            ("💹", "Trading"),
            ("🔔", "Alerts"),
            ("⚠️", "Risk"),
            ("⚙️", "Settings"),
            ("ℹ️", "About")
        ]
        for idx, (icon, label) in enumerate(sidebar_items):
            btn = QPushButton(f"{icon}  {label}")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setCheckable(True)
            btn.setStyleSheet(
                f"QPushButton {{background: transparent; color: #e6e6e6; border: none; border-radius: 4px; padding: 14px 18px; margin: 0 8px; font-size: 16px; font-weight: 600; text-align: left; transition: background 0.2s, color 0.2s;}} "
                f"QPushButton:checked {{background: #23272a; color: {COLORS['yellow']};}} "
                f"QPushButton:hover {{background: #23272a; color: {COLORS['blue_light']};}}"
            )
            btn.clicked.connect(lambda checked, i=idx: self.set_page(i))
            sidebar_layout.addWidget(btn)
            self.sidebar_buttons.append(btn)
        sidebar_layout.addStretch()

        # App logo at the top
        logo = QLabel("<b style='font-size:28px; color:white;'>AlphaFlow</b>")
        logo.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        logo.setStyleSheet("margin-bottom: 32px;")
        sidebar_layout.insertWidget(0, logo)

        # Main content area (stacked pages)
        from PyQt6.QtWidgets import QStackedWidget
        self.pages = QStackedWidget()
        self.dashboard = DashboardPage()
        self.analysis = AnalysisPage()
        self.portfolio = PortfolioPage()
        self.backtest = BacktestPage()
        self.trading = TradingPage()
        self.alerts = AlertsPage()
        self.risk = RiskPage()
        self.settings = SettingsPage()
        self.about = AboutPage()
        self.pages.addWidget(self.dashboard)
        self.pages.addWidget(self.analysis)
        self.pages.addWidget(self.portfolio)
        self.pages.addWidget(self.backtest)
        self.pages.addWidget(self.trading)
        self.pages.addWidget(self.alerts)
        self.pages.addWidget(self.risk)
        self.pages.addWidget(self.settings)
        self.pages.addWidget(self.about)

        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.pages)
        main_layout.setStretch(0, 0)
        main_layout.setStretch(1, 1)

        # Set default page
        self.set_page(0)

    def set_page(self, idx):
        """Switch to the selected page and update sidebar highlight."""
        self.pages.setCurrentIndex(idx)
        for i, btn in enumerate(self.sidebar_buttons):
            btn.setChecked(i == idx)

    def create_menu_bar(self):
        """Create the native menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")

        refresh_action = QAction("Refresh Data", self)
        refresh_action.setShortcut("Cmd+R")
        refresh_action.triggered.connect(self.refresh_data)
        file_menu.addAction(refresh_action)

        file_menu.addSeparator()

        quit_action = QAction("Quit AlphaFlow", self)
        quit_action.setShortcut("Cmd+Q")
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        # View menu
        view_menu = menubar.addMenu("View")

        dashboard_action = QAction("Dashboard", self)
        dashboard_action.setShortcut("Cmd+1")
        dashboard_action.triggered.connect(lambda: self.tabs.setCurrentIndex(0))
        view_menu.addAction(dashboard_action)

        analysis_action = QAction("Analysis", self)
        analysis_action.setShortcut("Cmd+2")
        analysis_action.triggered.connect(lambda: self.tabs.setCurrentIndex(1))
        view_menu.addAction(analysis_action)

        settings_action = QAction("Settings", self)
        settings_action.setShortcut("Cmd+,")
        settings_action.triggered.connect(lambda: self.tabs.setCurrentIndex(2))
        view_menu.addAction(settings_action)

        # Window menu
        window_menu = menubar.addMenu("Window")

        minimize_action = QAction("Minimize", self)
        minimize_action.setShortcut("Cmd+M")
        minimize_action.triggered.connect(self.showMinimized)
        window_menu.addAction(minimize_action)

        # Help menu
        help_menu = menubar.addMenu("Help")

        about_action = QAction("About AlphaFlow", self)
        about_action.triggered.connect(lambda: self.tabs.setCurrentIndex(3))
        help_menu.addAction(about_action)

    def create_status_bar(self):
        """Create the status bar."""
        self.status_bar = self.statusBar()
        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(200)
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)

    def refresh_data(self):
        """Refresh market data."""
        if self.worker and self.worker.isRunning():
            return

        self.status_label.setText("Fetching data...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        self.worker = DataWorker(self.current_watchlist)
        self.worker.data_ready.connect(self.on_data_ready)
        self.worker.progress.connect(self.on_progress)
        self.worker.start()

    def on_data_ready(self, data: Dict):
        """Handle data fetch complete."""
        self.data = data
        self.dashboard.update_data(data)
        self.analysis.update_data(data)

        self.progress_bar.setVisible(False)
        self.status_label.setText(f"Updated: {datetime.now().strftime('%H:%M:%S')}")

    def on_progress(self, value: int):
        """Update progress bar."""
        self.progress_bar.setValue(value)

    def change_watchlist(self, name: str):
        """Change the current watchlist."""
        if name in WATCHLISTS:
            self.current_watchlist = WATCHLISTS[name]
        else:
            self.current_watchlist = WATCHLISTS.get('tech', ['AAPL', 'GOOGL', 'MSFT'])
        self.refresh_data()


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Main entry point."""
    logger.info("🚀 Starting AlphaFlow Native App...")

    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("AlphaFlow")
    app.setOrganizationName("The Align Project")
    app.setOrganizationDomain("alignproject.com")

    # Set style
    app.setStyle(QStyleFactory.create("Fusion"))
    app.setStyleSheet(DARK_STYLESHEET)

    # Create and show window
    window = AlphaFlowWindow()
    window.show()

    logger.info("✅ AlphaFlow is running!")

    # Run event loop
    sys.exit(app.exec())


if __name__ == '__main__':
    main()

"""Chart panel widget with candlestick charts and technical indicators."""

import logging
from typing import Optional, Dict, List
from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QComboBox, QLabel, QSplitter
)
from PyQt6.QtCore import Qt, QPointF, pyqtSignal
from PyQt6.QtCharts import (
    QChart, QChartView, QCandlestickSeries, QCandlestickSet,
    QBarSeries, QBarSet, QDateTimeAxis, QValueAxis,
    QLineSeries
)
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush
import pandas as pd

from app.styles.colors import COLORS


class ChartPanel(QWidget):
    """
    Professional chart panel with candlestick charts and technical indicators.

    Features:
    - Candlestick price chart
    - Volume bars
    - Technical indicator overlays (SMA, EMA, Bollinger Bands)
    - Interactive crosshair (future enhancement)
    - Timeframe selection
    """

    timeframe_changed = pyqtSignal(str)  # timeframe selected

    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)

        # Data storage
        self.symbol: Optional[str] = None
        self.df: Optional[pd.DataFrame] = None

        # Chart components
        self.price_chart: Optional[QChart] = None
        self.volume_chart: Optional[QChart] = None
        self.candlestick_series: Optional[QCandlestickSeries] = None
        self.volume_series: Optional[QBarSeries] = None

        # Indicator series
        self.indicator_series: Dict[str, QLineSeries] = {}

        self._init_ui()

    def _init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Toolbar
        toolbar = self._create_toolbar()
        layout.addWidget(toolbar)

        # Chart area (split into price chart and volume chart)
        splitter = QSplitter(Qt.Orientation.Vertical)

        # Price chart
        self.price_chart_view = self._create_price_chart()
        splitter.addWidget(self.price_chart_view)

        # Volume chart
        self.volume_chart_view = self._create_volume_chart()
        splitter.addWidget(self.volume_chart_view)

        # Set size ratio (price chart takes 70%, volume takes 30%)
        splitter.setSizes([700, 300])

        layout.addWidget(splitter)

    def _create_toolbar(self) -> QWidget:
        """Create chart toolbar with controls."""
        toolbar = QWidget()
        toolbar.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['bg_secondary']};
                border-bottom: 1px solid {COLORS['border']};
            }}
        """)

        layout = QHBoxLayout(toolbar)
        layout.setContentsMargins(12, 8, 12, 8)

        # Symbol label
        self.symbol_label = QLabel("No Symbol Selected")
        self.symbol_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text_primary']};
                font-size: 14px;
                font-weight: 600;
            }}
        """)
        layout.addWidget(self.symbol_label)

        layout.addStretch()

        # Timeframe selector
        layout.addWidget(QLabel("Timeframe:"))
        self.timeframe_combo = QComboBox()
        self.timeframe_combo.addItems(['1D', '5D', '1M', '3M', '6M', '1Y', 'YTD', 'ALL'])
        self.timeframe_combo.setCurrentText('3M')
        self.timeframe_combo.currentTextChanged.connect(self.timeframe_changed.emit)
        layout.addWidget(self.timeframe_combo)

        # Indicator toggles
        self.sma_20_btn = self._create_indicator_button("SMA 20", COLORS['neutral'])
        self.sma_50_btn = self._create_indicator_button("SMA 50", COLORS['accent_alt'])
        self.bollinger_btn = self._create_indicator_button("BB", COLORS['accent_gold'])

        layout.addWidget(self.sma_20_btn)
        layout.addWidget(self.sma_50_btn)
        layout.addWidget(self.bollinger_btn)

        return toolbar

    def _create_indicator_button(self, text: str, color: str) -> QPushButton:
        """Create a toggle button for an indicator."""
        btn = QPushButton(text)
        btn.setCheckable(True)
        btn.setChecked(False)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['bg_elevated']};
                color: {COLORS['text_secondary']};
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
                padding: 4px 12px;
                font-size: 12px;
            }}
            QPushButton:checked {{
                background-color: {color};
                color: {COLORS['text_primary']};
                border-color: {color};
            }}
            QPushButton:hover {{
                border-color: {color};
            }}
        """)
        btn.toggled.connect(lambda checked: self._toggle_indicator(text, checked))
        return btn

    def _create_price_chart(self) -> QChartView:
        """Create the candlestick price chart."""
        # Create chart
        self.price_chart = QChart()
        self.price_chart.setTitle("")
        self.price_chart.setAnimationOptions(QChart.AnimationOption.NoAnimation)
        self.price_chart.setBackgroundBrush(QBrush(QColor(COLORS['bg_primary'])))
        self.price_chart.setPlotAreaBackgroundBrush(QBrush(QColor(COLORS['bg_secondary'])))
        self.price_chart.setPlotAreaBackgroundVisible(True)

        # Create chart view
        chart_view = QChartView(self.price_chart)
        chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)

        return chart_view

    def _create_volume_chart(self) -> QChartView:
        """Create the volume bar chart."""
        # Create chart
        self.volume_chart = QChart()
        self.volume_chart.setTitle("")
        self.volume_chart.setAnimationOptions(QChart.AnimationOption.NoAnimation)
        self.volume_chart.setBackgroundBrush(QBrush(QColor(COLORS['bg_primary'])))
        self.volume_chart.setPlotAreaBackgroundBrush(QBrush(QColor(COLORS['bg_secondary'])))
        self.volume_chart.setPlotAreaBackgroundVisible(True)

        # Create chart view
        chart_view = QChartView(self.volume_chart)
        chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        chart_view.setMaximumHeight(200)

        return chart_view

    def update_data(self, symbol: str, data: dict):
        """
        Update chart with new data.

        Args:
            symbol: Stock symbol
            data: Data dictionary with 'historical' DataFrame
        """
        self.symbol = symbol
        self.df = data.get('historical')

        if self.df is None or len(self.df) == 0:
            self.logger.warning(f"No data available for {symbol}")
            return

        # Update symbol label
        self.symbol_label.setText(symbol)

        # Update charts
        self._update_candlestick_chart()
        self._update_volume_chart()

        # Update any active indicators
        if self.sma_20_btn.isChecked():
            self._add_sma_indicator(20)
        if self.sma_50_btn.isChecked():
            self._add_sma_indicator(50)
        if self.bollinger_btn.isChecked():
            self._add_bollinger_bands()

    def _update_candlestick_chart(self):
        """Update the candlestick price chart."""
        if self.df is None:
            return

        # Clear existing series
        self.price_chart.removeAllSeries()
        self.indicator_series.clear()

        # Create candlestick series
        self.candlestick_series = QCandlestickSeries()
        self.candlestick_series.setName("Price")

        # Set colors
        self.candlestick_series.setIncreasingColor(QColor(COLORS['positive']))
        self.candlestick_series.setDecreasingColor(QColor(COLORS['negative']))

        # Add candlestick sets
        for idx, row in self.df.iterrows():
            candlestick_set = QCandlestickSet(
                float(row['open']),
                float(row['high']),
                float(row['low']),
                float(row['close']),
                idx.timestamp() * 1000  # Convert to milliseconds
            )
            self.candlestick_series.append(candlestick_set)

        # Add series to chart
        self.price_chart.addSeries(self.candlestick_series)

        # Create axes
        self._create_price_axes()

    def _create_price_axes(self):
        """Create axes for the price chart."""
        if self.df is None or self.candlestick_series is None:
            return

        # Remove old axes
        for axis in self.price_chart.axes():
            self.price_chart.removeAxis(axis)

        # X-axis (time)
        axis_x = QDateTimeAxis()
        axis_x.setFormat("MMM dd")
        axis_x.setTitleText("Date")
        axis_x.setLabelsColor(QColor(COLORS['text_secondary']))
        axis_x.setGridLineColor(QColor(COLORS['border']))

        # Y-axis (price)
        axis_y = QValueAxis()
        axis_y.setLabelFormat("%.2f")
        axis_y.setTitleText("Price ($)")
        axis_y.setLabelsColor(QColor(COLORS['text_secondary']))
        axis_y.setGridLineColor(QColor(COLORS['border']))

        # Set ranges
        min_date = self.df.index.min()
        max_date = self.df.index.max()
        axis_x.setMin(min_date)
        axis_x.setMax(max_date)

        min_price = self.df['low'].min() * 0.99
        max_price = self.df['high'].max() * 1.01
        axis_y.setMin(min_price)
        axis_y.setMax(max_price)

        # Add axes to chart
        self.price_chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        self.price_chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)

        # Attach series to axes
        self.candlestick_series.attachAxis(axis_x)
        self.candlestick_series.attachAxis(axis_y)

    def _update_volume_chart(self):
        """Update the volume bar chart."""
        if self.df is None or 'volume' not in self.df.columns:
            return

        # Clear existing series
        self.volume_chart.removeAllSeries()

        # Create bar series
        self.volume_series = QBarSeries()
        bar_set = QBarSet("Volume")

        # Set color based on price direction
        bar_set.setColor(QColor(COLORS['neutral']))

        # Add volume data
        for idx, row in self.df.iterrows():
            bar_set.append(float(row['volume']))

        self.volume_series.append(bar_set)

        # Add series to chart
        self.volume_chart.addSeries(self.volume_series)

        # Create axes
        self._create_volume_axes()

    def _create_volume_axes(self):
        """Create axes for the volume chart."""
        if self.df is None or self.volume_series is None:
            return

        # Remove old axes
        for axis in self.volume_chart.axes():
            self.volume_chart.removeAxis(axis)

        # X-axis (time)
        axis_x = QDateTimeAxis()
        axis_x.setFormat("MMM dd")
        axis_x.setLabelsColor(QColor(COLORS['text_secondary']))
        axis_x.setGridLineColor(QColor(COLORS['border']))

        # Y-axis (volume)
        axis_y = QValueAxis()
        axis_y.setLabelFormat("%.0f")
        axis_y.setTitleText("Volume")
        axis_y.setLabelsColor(QColor(COLORS['text_secondary']))
        axis_y.setGridLineColor(QColor(COLORS['border']))

        # Set ranges
        min_date = self.df.index.min()
        max_date = self.df.index.max()
        axis_x.setMin(min_date)
        axis_x.setMax(max_date)

        max_volume = self.df['volume'].max() * 1.1
        axis_y.setMin(0)
        axis_y.setMax(max_volume)

        # Add axes to chart
        self.volume_chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        self.volume_chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)

        # Attach series to axes
        self.volume_series.attachAxis(axis_x)
        self.volume_series.attachAxis(axis_y)

    def _toggle_indicator(self, indicator_name: str, enabled: bool):
        """Toggle an indicator on/off."""
        if not enabled:
            # Remove indicator
            if indicator_name in self.indicator_series:
                series = self.indicator_series[indicator_name]
                self.price_chart.removeSeries(series)
                del self.indicator_series[indicator_name]
        else:
            # Add indicator
            if "SMA" in indicator_name:
                period = int(indicator_name.split()[-1])
                self._add_sma_indicator(period)
            elif "BB" in indicator_name:
                self._add_bollinger_bands()

    def _add_sma_indicator(self, period: int):
        """Add SMA indicator to chart."""
        if self.df is None:
            return

        col_name = f'sma_{period}'
        if col_name not in self.df.columns:
            self.logger.warning(f"SMA {period} not available in data")
            return

        # Create line series
        series = QLineSeries()
        series.setName(f"SMA {period}")

        # Set color
        color = COLORS['neutral'] if period == 20 else COLORS['accent_alt']
        pen = QPen(QColor(color))
        pen.setWidth(2)
        series.setPen(pen)

        # Add data points
        for idx, row in self.df.iterrows():
            if pd.notna(row[col_name]):
                series.append(QPointF(idx.timestamp() * 1000, float(row[col_name])))

        # Add to chart
        self.price_chart.addSeries(series)

        # Attach to existing axes
        axes = self.price_chart.axes()
        if len(axes) >= 2:
            series.attachAxis(axes[0])  # X-axis
            series.attachAxis(axes[1])  # Y-axis

        # Store reference
        self.indicator_series[f"SMA {period}"] = series

    def _add_bollinger_bands(self):
        """Add Bollinger Bands to chart."""
        if self.df is None:
            return

        # Check if Bollinger Bands columns exist
        if 'bb_upper' not in self.df.columns or 'bb_lower' not in self.df.columns:
            self.logger.warning("Bollinger Bands not available in data")
            return

        # Create upper band series
        upper_series = QLineSeries()
        upper_series.setName("BB Upper")
        pen = QPen(QColor(COLORS['accent_gold']))
        pen.setWidth(1)
        pen.setStyle(Qt.PenStyle.DashLine)
        upper_series.setPen(pen)

        # Create lower band series
        lower_series = QLineSeries()
        lower_series.setName("BB Lower")
        lower_series.setPen(pen)

        # Add data points
        for idx, row in self.df.iterrows():
            if pd.notna(row['bb_upper']):
                upper_series.append(QPointF(idx.timestamp() * 1000, float(row['bb_upper'])))
            if pd.notna(row['bb_lower']):
                lower_series.append(QPointF(idx.timestamp() * 1000, float(row['bb_lower'])))

        # Add to chart
        self.price_chart.addSeries(upper_series)
        self.price_chart.addSeries(lower_series)

        # Attach to existing axes
        axes = self.price_chart.axes()
        if len(axes) >= 2:
            upper_series.attachAxis(axes[0])
            upper_series.attachAxis(axes[1])
            lower_series.attachAxis(axes[0])
            lower_series.attachAxis(axes[1])

        # Store references
        self.indicator_series["BB Upper"] = upper_series
        self.indicator_series["BB Lower"] = lower_series

    def clear(self):
        """Clear all chart data."""
        self.symbol = None
        self.df = None
        self.price_chart.removeAllSeries()
        self.volume_chart.removeAllSeries()
        self.indicator_series.clear()
        self.symbol_label.setText("No Symbol Selected")

"""Analytics page with comprehensive portfolio analysis and risk metrics."""

import logging
from typing import Optional, Dict, List
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QLabel, QSplitter, QScrollArea, QTabWidget
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtCharts import QChart, QChartView, QLineSeries, QPieSeries, QBarSeries, QBarSet
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush

from app.styles.colors import COLORS
from app.widgets import MetricCard, BloombergDataGrid


class AnalyticsPage(QWidget):
    """
    Comprehensive analytics page with portfolio analysis and risk metrics.

    Features:
    - Portfolio performance overview
    - Position breakdown with allocation
    - Risk metrics (Sharpe, Sortino, Beta, VaR)
    - Correlation matrix
    - Historical performance charts
    - Detailed position analysis
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)

        # Sample portfolio data
        self.positions = {
            'AAPL': {'quantity': 50, 'avg_price': 180.50, 'current_price': 185.25},
            'MSFT': {'quantity': 30, 'avg_price': 375.00, 'current_price': 380.15},
            'GOOGL': {'quantity': 20, 'avg_price': 140.25, 'current_price': 142.50},
            'TSLA': {'quantity': 15, 'avg_price': 245.00, 'current_price': 238.75},
        }

        self._init_ui()
        self._populate_data()

    def _init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # Title
        title = QLabel("Portfolio Analytics")
        title.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text_primary']};
                font-size: 24px;
                font-weight: 700;
            }}
        """)
        layout.addWidget(title)

        # Performance metrics row
        metrics_layout = QHBoxLayout()

        self.portfolio_value_card = MetricCard("Portfolio Value", "$0.00", 0.0)
        self.total_gain_card = MetricCard("Total Gain", "$0.00", 0.0)
        self.total_return_card = MetricCard("Total Return", "0.00%", 0.0)
        self.sharpe_ratio_card = MetricCard("Sharpe Ratio", "0.00", 0.0)

        metrics_layout.addWidget(self.portfolio_value_card)
        metrics_layout.addWidget(self.total_gain_card)
        metrics_layout.addWidget(self.total_return_card)
        metrics_layout.addWidget(self.sharpe_ratio_card)

        layout.addLayout(metrics_layout)

        # Tab widget for different analytics views
        self.tab_widget = QTabWidget()
        self.tab_widget.setDocumentMode(True)

        # Add tabs
        self.tab_widget.addTab(self._create_positions_tab(), "Positions")
        self.tab_widget.addTab(self._create_risk_metrics_tab(), "Risk Metrics")
        self.tab_widget.addTab(self._create_performance_tab(), "Performance")

        layout.addWidget(self.tab_widget)

    def _create_positions_tab(self) -> QWidget:
        """Create positions analysis tab."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 16, 0, 0)

        # Left: Positions table
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(12)

        positions_label = QLabel("Open Positions")
        positions_label.setStyleSheet(f"color: {COLORS['text_primary']}; font-weight: 600; font-size: 16px;")
        left_layout.addWidget(positions_label)

        self.positions_grid = BloombergDataGrid()
        self.positions_grid.set_columns([
            'Symbol', 'Quantity', 'Avg Price', 'Current Price',
            'Market Value', 'Cost Basis', 'P&L', 'P&L %', 'Weight %'
        ])
        left_layout.addWidget(self.positions_grid)

        # Right: Allocation chart
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(12)

        allocation_label = QLabel("Portfolio Allocation")
        allocation_label.setStyleSheet(f"color: {COLORS['text_primary']}; font-weight: 600; font-size: 16px;")
        right_layout.addWidget(allocation_label)

        self.allocation_chart_view = self._create_allocation_chart()
        right_layout.addWidget(self.allocation_chart_view)

        # Sector allocation (placeholder)
        sector_label = QLabel("Sector Breakdown")
        sector_label.setStyleSheet(f"color: {COLORS['text_primary']}; font-weight: 600; font-size: 14px;")
        right_layout.addWidget(sector_label)

        self.sector_grid = BloombergDataGrid()
        self.sector_grid.set_columns(['Sector', 'Value', 'Weight %'])
        self.sector_grid.setMaximumHeight(200)
        right_layout.addWidget(self.sector_grid)

        # Add panels to splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([600, 400])

        layout.addWidget(splitter)

        return widget

    def _create_risk_metrics_tab(self) -> QWidget:
        """Create risk metrics tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 16, 0, 0)
        layout.setSpacing(16)

        # Risk metrics cards
        metrics_row1 = QHBoxLayout()

        self.beta_card = MetricCard("Beta", "0.00", 0.0)
        self.alpha_card = MetricCard("Alpha", "0.00%", 0.0)
        self.volatility_card = MetricCard("Volatility", "0.00%", 0.0)
        self.sortino_card = MetricCard("Sortino Ratio", "0.00", 0.0)

        metrics_row1.addWidget(self.beta_card)
        metrics_row1.addWidget(self.alpha_card)
        metrics_row1.addWidget(self.volatility_card)
        metrics_row1.addWidget(self.sortino_card)

        layout.addLayout(metrics_row1)

        # VaR and Risk metrics
        metrics_row2 = QHBoxLayout()

        self.var_1day_card = MetricCard("VaR (1-day)", "$0.00", 0.0)
        self.var_10day_card = MetricCard("VaR (10-day)", "$0.00", 0.0)
        self.max_drawdown_card = MetricCard("Max Drawdown", "0.00%", 0.0)
        self.recovery_days_card = MetricCard("Recovery Days", "0", 0.0)

        metrics_row2.addWidget(self.var_1day_card)
        metrics_row2.addWidget(self.var_10day_card)
        metrics_row2.addWidget(self.max_drawdown_card)
        metrics_row2.addWidget(self.recovery_days_card)

        layout.addLayout(metrics_row2)

        # Correlation matrix
        corr_label = QLabel("Position Correlation Matrix")
        corr_label.setStyleSheet(f"color: {COLORS['text_primary']}; font-weight: 600; font-size: 16px;")
        layout.addWidget(corr_label)

        self.correlation_grid = BloombergDataGrid()
        self.correlation_grid.set_columns(['Symbol', 'AAPL', 'MSFT', 'GOOGL', 'TSLA'])
        layout.addWidget(self.correlation_grid)

        # Risk concentration
        risk_label = QLabel("Risk Concentration")
        risk_label.setStyleSheet(f"color: {COLORS['text_primary']}; font-weight: 600; font-size: 16px;")
        layout.addWidget(risk_label)

        risk_info = QLabel(
            "• Largest position: 35% (within 40% limit)\n"
            "• Top 3 positions: 68% (within 75% limit)\n"
            "• Sector concentration: Technology 85% ⚠️\n"
            "• Daily VaR as % of portfolio: 2.1% (within 5% limit)"
        )
        risk_info.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text_secondary']};
                background-color: {COLORS['bg_elevated']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 16px;
                font-size: 13px;
                line-height: 1.6;
            }}
        """)
        layout.addWidget(risk_info)

        layout.addStretch()

        return widget

    def _create_performance_tab(self) -> QWidget:
        """Create performance analysis tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 16, 0, 0)
        layout.setSpacing(16)

        # Performance period selector would go here
        period_label = QLabel("Historical Performance")
        period_label.setStyleSheet(f"color: {COLORS['text_primary']}; font-weight: 600; font-size: 16px;")
        layout.addWidget(period_label)

        # Performance chart
        self.performance_chart_view = self._create_performance_chart()
        layout.addWidget(self.performance_chart_view)

        # Monthly returns table
        monthly_label = QLabel("Monthly Returns")
        monthly_label.setStyleSheet(f"color: {COLORS['text_primary']}; font-weight: 600; font-size: 16px;")
        layout.addWidget(monthly_label)

        self.monthly_returns_grid = BloombergDataGrid()
        self.monthly_returns_grid.set_columns([
            'Month', 'Return %', 'Benchmark %', 'Alpha %', 'Trades', 'Win Rate %'
        ])
        layout.addWidget(self.monthly_returns_grid)

        return widget

    def _create_allocation_chart(self) -> QChartView:
        """Create portfolio allocation pie chart."""
        self.allocation_chart = QChart()
        self.allocation_chart.setTitle("")
        self.allocation_chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        self.allocation_chart.setBackgroundBrush(QBrush(QColor(COLORS['bg_secondary'])))
        self.allocation_chart.legend().setVisible(True)
        self.allocation_chart.legend().setAlignment(Qt.AlignmentFlag.AlignRight)

        chart_view = QChartView(self.allocation_chart)
        chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        chart_view.setMinimumHeight(300)

        return chart_view

    def _create_performance_chart(self) -> QChartView:
        """Create historical performance chart."""
        self.performance_chart = QChart()
        self.performance_chart.setTitle("")
        self.performance_chart.setAnimationOptions(QChart.AnimationOption.NoAnimation)
        self.performance_chart.setBackgroundBrush(QBrush(QColor(COLORS['bg_secondary'])))
        self.performance_chart.setPlotAreaBackgroundBrush(QBrush(QColor(COLORS['bg_elevated'])))
        self.performance_chart.setPlotAreaBackgroundVisible(True)

        chart_view = QChartView(self.performance_chart)
        chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        chart_view.setMinimumHeight(300)

        return chart_view

    def _populate_data(self):
        """Populate sample data."""
        # Calculate portfolio metrics
        total_value = 0
        total_cost = 0

        for symbol, pos in self.positions.items():
            market_value = pos['quantity'] * pos['current_price']
            cost_basis = pos['quantity'] * pos['avg_price']
            total_value += market_value
            total_cost += cost_basis

        total_gain = total_value - total_cost
        total_return_pct = (total_gain / total_cost * 100) if total_cost > 0 else 0

        # Update summary metrics
        self.portfolio_value_card.set_value(f"${total_value:,.2f}", 0.0)
        self.total_gain_card.set_value(f"${total_gain:+,.2f}", total_gain)
        self.total_return_card.set_value(f"{total_return_pct:+.2f}%", total_return_pct)
        self.sharpe_ratio_card.set_value("1.85", 1.85)

        # Populate positions table
        for symbol, pos in self.positions.items():
            market_value = pos['quantity'] * pos['current_price']
            cost_basis = pos['quantity'] * pos['avg_price']
            pnl = market_value - cost_basis
            pnl_pct = (pnl / cost_basis * 100) if cost_basis > 0 else 0
            weight_pct = (market_value / total_value * 100) if total_value > 0 else 0

            self.positions_grid.add_row({
                'Symbol': symbol,
                'Quantity': pos['quantity'],
                'Avg Price': pos['avg_price'],
                'Current Price': pos['current_price'],
                'Market Value': market_value,
                'Cost Basis': cost_basis,
                'P&L': pnl,
                'P&L %': pnl_pct,
                'Weight %': weight_pct,
            })

        # Create allocation pie chart
        self._update_allocation_chart()

        # Populate sector breakdown (sample data)
        self.sector_grid.add_row({
            'Sector': 'Technology',
            'Value': total_value * 0.85,
            'Weight %': 85.0,
        })
        self.sector_grid.add_row({
            'Sector': 'Consumer',
            'Value': total_value * 0.15,
            'Weight %': 15.0,
        })

        # Populate risk metrics with sample values
        self.beta_card.set_value("1.12", 1.12)
        self.alpha_card.set_value("+3.5%", 3.5)
        self.volatility_card.set_value("18.2%", 18.2)
        self.sortino_card.set_value("2.15", 2.15)

        self.var_1day_card.set_value("-$1,250", -1250)
        self.var_10day_card.set_value("-$3,950", -3950)
        self.max_drawdown_card.set_value("-12.5%", -12.5)
        self.recovery_days_card.set_value("23", 0.0)

        # Populate correlation matrix (sample data)
        correlations = {
            'AAPL': [1.00, 0.75, 0.68, 0.45],
            'MSFT': [0.75, 1.00, 0.82, 0.52],
            'GOOGL': [0.68, 0.82, 1.00, 0.48],
            'TSLA': [0.45, 0.52, 0.48, 1.00],
        }

        for i, symbol in enumerate(['AAPL', 'MSFT', 'GOOGL', 'TSLA']):
            row_data = {'Symbol': symbol}
            for j, col_symbol in enumerate(['AAPL', 'MSFT', 'GOOGL', 'TSLA']):
                row_data[col_symbol] = correlations[symbol][j]
            self.correlation_grid.add_row(row_data)

        # Populate monthly returns (sample data)
        months = ['Jan 2026', 'Dec 2025', 'Nov 2025', 'Oct 2025', 'Sep 2025']
        returns = [+5.2, +3.1, -2.4, +4.8, +1.9]
        benchmark = [+4.1, +2.8, -1.9, +3.9, +2.1]

        for month, ret, bench in zip(months, returns, benchmark):
            alpha = ret - bench
            self.monthly_returns_grid.add_row({
                'Month': month,
                'Return %': ret,
                'Benchmark %': bench,
                'Alpha %': alpha,
                'Trades': np.random.randint(15, 45),
                'Win Rate %': np.random.uniform(55, 75),
            })

    def _update_allocation_chart(self):
        """Update the allocation pie chart."""
        # Calculate total value
        total_value = sum(
            pos['quantity'] * pos['current_price']
            for pos in self.positions.values()
        )

        # Create pie series
        series = QPieSeries()

        colors = [
            QColor(COLORS['accent_blue']),
            QColor(COLORS['positive']),
            QColor(COLORS['accent_purple']),
            QColor(COLORS['accent_gold']),
        ]

        for i, (symbol, pos) in enumerate(self.positions.items()):
            market_value = pos['quantity'] * pos['current_price']
            percentage = (market_value / total_value * 100) if total_value > 0 else 0

            slice = series.append(f"{symbol} ({percentage:.1f}%)", market_value)
            slice.setColor(colors[i % len(colors)])
            slice.setLabelVisible(True)

        self.allocation_chart.removeAllSeries()
        self.allocation_chart.addSeries(series)

    def update_positions(self, positions: Dict):
        """Update positions data."""
        self.positions = positions
        self.positions_grid.clear_data()
        self._populate_data()

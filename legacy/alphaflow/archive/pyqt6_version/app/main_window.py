"""Main window for AlphaFlow Trading Platform."""

import sys
import logging
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QMenuBar, QStatusBar, QLabel, QPushButton,
    QMessageBox
)
from PyQt6.QtCore import Qt, QTimer, QSettings
from PyQt6.QtGui import QAction, QKeySequence

from app.styles import get_stylesheet, COLORS
from app.widgets import MetricCard, StatusBadge, BloombergDataGrid, OrderEntryDialog
from app.controllers import DataController, TradingController
from app.pages import TradingPage, SettingsPage, BacktestPage, StrategyPage, AnalyticsPage
from core import (
    TradingMode, TradingConfig, setup_logging, WATCHLISTS,
    is_market_open, get_market_status_message,
    AlertManager, Alert, AlertType
)


class AlphaFlowMainWindow(QMainWindow):
    """
    Main window for AlphaFlow Trading Platform.

    Provides a Bloomberg Terminal-style interface with:
    - Professional dark theme
    - Multi-panel layout
    - Real-time data display
    - Trading capabilities
    """

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)

        # Application state
        self.trading_mode = TradingMode.PAPER
        self.settings = QSettings('AlphaFlow', 'TradingPlatform')

        # Initialize controllers
        self.data_controller = DataController(use_alpaca=True)
        self.trading_controller = TradingController(self.trading_mode)
        self.alert_manager = AlertManager()

        # Connect controller signals
        self._connect_controller_signals()

        # Setup
        self._setup_window()
        self._create_menu_bar()
        self._create_central_widget()
        self._create_status_bar()
        self._setup_keyboard_shortcuts()
        self._start_update_timers()

        # Initialize with default watchlist
        self._load_watchlist()

        self.logger.info("AlphaFlow initialized")

    def _connect_controller_signals(self):
        """Connect controller signals to UI update methods."""
        # Data controller signals
        self.data_controller.data_updated.connect(self._on_data_updated)
        self.data_controller.error_occurred.connect(self._on_data_error)

        # Trading controller signals
        self.trading_controller.order_placed.connect(self._on_order_placed)
        self.trading_controller.order_filled.connect(self._on_order_filled)
        self.trading_controller.order_rejected.connect(self._on_order_rejected)
        self.trading_controller.error_occurred.connect(self._on_trading_error)

        # Alert manager signals
        self.alert_manager.alert_triggered.connect(self._on_alert_triggered)

        # Connect data updates to alert manager
        self.data_controller.data_updated.connect(self.alert_manager.update_market_data)

    def _load_watchlist(self):
        """Load default watchlist and start fetching data."""
        default_watchlist = WATCHLISTS.get('tech', ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA'])
        self.data_controller.set_watchlist(default_watchlist)
        self.data_controller.fetch_symbols(default_watchlist, self._on_initial_data_loaded)

    def _on_initial_data_loaded(self):
        """Handle initial data load complete."""
        self.logger.info("Initial watchlist data loaded")
        self._update_dashboard_from_cache()
        # Start auto-refresh (every 60 seconds)
        self.data_controller.start_auto_refresh(60000)

    def _on_data_updated(self, symbol: str, data: dict):
        """Handle data update for a symbol."""
        self._update_watchlist_row(symbol, data)

    def _on_data_error(self, symbol: str, error: str):
        """Handle data fetch error."""
        self.logger.error(f"Data error for {symbol}: {error}")

    def _on_order_placed(self, order):
        """Handle order placed successfully."""
        self.statusBar().showMessage(f"Order placed: {order.side.value} {order.quantity} {order.symbol}", 3000)
        self._update_orders_tab()

    def _on_order_filled(self, order):
        """Handle order filled."""
        self.statusBar().showMessage(f"Order filled: {order.symbol} @ ${order.filled_avg_price:.2f}", 5000)
        self._update_positions_tab()
        self._update_dashboard_metrics()

    def _on_order_rejected(self, order, reason: str):
        """Handle order rejected."""
        QMessageBox.warning(self, "Order Rejected", f"Order rejected: {reason}")

    def _on_trading_error(self, error: str):
        """Handle trading error."""
        QMessageBox.critical(self, "Trading Error", error)

    def _setup_window(self):
        """Setup main window properties."""
        self.setWindowTitle("AlphaFlow | Professional Trading Platform v6.3.0")
        self.setMinimumSize(1600, 1000)

        # Apply Bloomberg-inspired stylesheet
        self.setStyleSheet(get_stylesheet())

        # Restore window geometry if available
        geometry = self.settings.value('geometry')
        if geometry:
            self.restoreGeometry(geometry)
        else:
            # Default size and position
            self.resize(1800, 1100)
            # Center on screen
            from PyQt6.QtWidgets import QApplication
            screen = QApplication.primaryScreen().geometry()
            x = (screen.width() - 1800) // 2
            y = (screen.height() - 1100) // 2
            self.move(x, y)

    def _create_menu_bar(self):
        """Create the application menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu('&File')

        new_order_action = QAction('&New Order', self)
        new_order_action.setShortcut(QKeySequence('Ctrl+N'))
        new_order_action.triggered.connect(self._on_new_order)
        file_menu.addAction(new_order_action)

        file_menu.addSeparator()

        refresh_action = QAction('&Refresh Data', self)
        refresh_action.setShortcut(QKeySequence('Ctrl+R'))
        refresh_action.triggered.connect(self._on_refresh_data)
        file_menu.addAction(refresh_action)

        file_menu.addSeparator()

        exit_action = QAction('E&xit', self)
        exit_action.setShortcut(QKeySequence('Ctrl+Q'))
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Trading menu
        trading_menu = menubar.addMenu('&Trading')

        paper_mode_action = QAction('&Paper Trading Mode', self)
        paper_mode_action.setCheckable(True)
        paper_mode_action.setChecked(self.trading_mode == TradingMode.PAPER)
        paper_mode_action.triggered.connect(lambda: self._set_trading_mode(TradingMode.PAPER))
        trading_menu.addAction(paper_mode_action)

        live_mode_action = QAction('&Live Trading Mode', self)
        live_mode_action.setCheckable(True)
        live_mode_action.setChecked(self.trading_mode == TradingMode.LIVE)
        live_mode_action.triggered.connect(lambda: self._set_trading_mode(TradingMode.LIVE))
        trading_menu.addAction(live_mode_action)

        # View menu
        view_menu = menubar.addMenu('&View')

        fullscreen_action = QAction('&Full Screen', self)
        fullscreen_action.setShortcut(QKeySequence('Ctrl+F'))
        fullscreen_action.setCheckable(True)
        fullscreen_action.triggered.connect(self._toggle_fullscreen)
        view_menu.addAction(fullscreen_action)

        # Help menu
        help_menu = menubar.addMenu('&Help')

        about_action = QAction('&About AlphaFlow', self)
        about_action.triggered.connect(self._show_about_dialog)
        help_menu.addAction(about_action)

    def _create_central_widget(self):
        """Create the central widget with tabs."""
        central_widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setDocumentMode(True)

        # Add tabs (clean, professional names without emojis)
        self.tab_widget.addTab(self._create_dashboard_tab(), "Dashboard")
        self.tab_widget.addTab(self._create_trading_tab(), "Trading")
        self.tab_widget.addTab(self._create_positions_tab(), "Analytics")
        self.tab_widget.addTab(self._create_orders_tab(), "Orders")
        self.tab_widget.addTab(self._create_strategies_tab(), "Strategies")
        self.tab_widget.addTab(self._create_backtest_tab(), "Backtest")
        self.tab_widget.addTab(self._create_settings_tab(), "Settings")

        layout.addWidget(self.tab_widget)
        central_widget.setLayout(layout)

        self.setCentralWidget(central_widget)

    def _create_dashboard_tab(self) -> QWidget:
        """Create the dashboard tab."""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        # Header
        header = QLabel("Portfolio Overview")
        header.setStyleSheet(f"""
            QLabel {{
                font-size: 24px;
                font-weight: 700;
                color: {COLORS['text_primary']};
                padding: 0px 0px 12px 0px;
                border-bottom: 2px solid {COLORS['border']};
            }}
        """)
        layout.addWidget(header)

        # Metrics row
        metrics_layout = QHBoxLayout()
        metrics_layout.setSpacing(16)

        self.portfolio_value_card = MetricCard("Portfolio Value", "$100,000.00", 0.0)
        self.day_pnl_card = MetricCard("Day P&L", "$0.00", 0.0)
        self.total_return_card = MetricCard("Total Return", "0.00%", 0.0)
        self.win_rate_card = MetricCard("Win Rate", "0.0%", 0.0)

        metrics_layout.addWidget(self.portfolio_value_card)
        metrics_layout.addWidget(self.day_pnl_card)
        metrics_layout.addWidget(self.total_return_card)
        metrics_layout.addWidget(self.win_rate_card)

        layout.addLayout(metrics_layout)

        # Watchlist grid
        watchlist_label = QLabel("Market Watchlist")
        watchlist_label.setStyleSheet(f"""
            QLabel {{
                font-size: 18px;
                font-weight: 700;
                color: {COLORS['text_primary']};
                padding: 20px 0px 8px 0px;
            }}
        """)
        layout.addWidget(watchlist_label)

        self.watchlist_grid = BloombergDataGrid()
        self.watchlist_grid.set_columns(
            ['Symbol', 'Price', 'Change', 'Change %', 'Volume'],
            numeric_columns=['Price', 'Change', 'Change %', 'Volume']
        )

        # Add sample data
        self._populate_sample_watchlist()

        layout.addWidget(self.watchlist_grid)

        layout.addStretch()

        widget.setLayout(layout)
        return widget

    def _create_trading_tab(self) -> QWidget:
        """Create the trading tab."""
        self.trading_page = TradingPage()

        # Connect trading page signals
        self.trading_page.symbol_changed.connect(self._on_trading_symbol_changed)
        self.trading_page.order_requested.connect(self._on_trading_order_requested)
        self.trading_page.data_refresh_requested.connect(self._on_trading_data_refresh)

        # Connect data updates to trading page
        self.data_controller.data_updated.connect(self.trading_page.update_data)

        return self.trading_page

    def _create_positions_tab(self) -> QWidget:
        """Create the positions/analytics tab."""
        self.analytics_page = AnalyticsPage()
        return self.analytics_page

    def _create_orders_tab(self) -> QWidget:
        """Create the orders tab."""
        widget = QWidget()
        layout = QVBoxLayout()

        label = QLabel("Order History")
        label.setStyleSheet(f"""
            QLabel {{
                font-size: 20px;
                font-weight: bold;
                color: {COLORS['text_primary']};
                padding: 16px;
            }}
        """)
        layout.addWidget(label)

        # Orders grid
        self.orders_grid = BloombergDataGrid()
        self.orders_grid.set_columns(
            ['Time', 'Symbol', 'Side', 'Quantity', 'Price', 'Status'],
            numeric_columns=['Quantity', 'Price']
        )

        layout.addWidget(self.orders_grid)

        widget.setLayout(layout)
        return widget

    def _create_strategies_tab(self) -> QWidget:
        """Create the strategies tab."""
        self.strategy_page = StrategyPage()

        # Connect strategy page signals
        self.strategy_page.strategy_started.connect(self._on_strategy_started)
        self.strategy_page.strategy_stopped.connect(self._on_strategy_stopped)

        return self.strategy_page

    def _create_backtest_tab(self) -> QWidget:
        """Create the backtest tab."""
        self.backtest_page = BacktestPage()

        # Connect backtest page signals
        self.backtest_page.backtest_started.connect(self._on_backtest_started)

        return self.backtest_page

    def _create_settings_tab(self) -> QWidget:
        """Create the settings tab."""
        self.settings_page = SettingsPage()

        # Connect settings page signals
        self.settings_page.settings_changed.connect(self._on_settings_changed)
        self.settings_page.test_connection_requested.connect(self._on_test_connection)

        return self.settings_page

    def _create_status_bar(self):
        """Create the status bar."""
        statusbar = self.statusBar()

        # Market status
        self.market_status_badge = StatusBadge('MARKET_CLOSED')
        statusbar.addPermanentWidget(self.market_status_badge)

        # Trading mode
        self.trading_mode_label = QLabel(f"Mode: {self.trading_mode.value.upper()}")
        self.trading_mode_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['warning']};
                font-weight: bold;
                padding: 4px 12px;
            }}
        """)
        statusbar.addPermanentWidget(self.trading_mode_label)

        # Connection status
        self.connection_status = StatusBadge('DISCONNECTED')
        statusbar.addPermanentWidget(self.connection_status)

    def _setup_keyboard_shortcuts(self):
        """Setup global keyboard shortcuts."""
        # Tab navigation (Cmd+1 through Cmd+6)
        for i in range(6):
            shortcut = QKeySequence(f'Ctrl+{i+1}')
            action = QAction(self)
            action.setShortcut(shortcut)
            action.triggered.connect(lambda checked, idx=i: self.tab_widget.setCurrentIndex(idx))
            self.addAction(action)

    def _start_update_timers(self):
        """Start timers for periodic updates."""
        # Update market status every 60 seconds
        self.market_status_timer = QTimer()
        self.market_status_timer.timeout.connect(self._update_market_status)
        self.market_status_timer.start(60000)  # 60 seconds

        # Initial update
        self._update_market_status()

    def _update_market_status(self):
        """Update market status indicator."""
        message = get_market_status_message()

        if is_market_open():
            self.market_status_badge.set_status('MARKET_OPEN')
        elif 'Pre-market' in message:
            self.market_status_badge.set_status('PRE_MARKET')
        elif 'After-hours' in message:
            self.market_status_badge.set_status('AFTER_HOURS')
        else:
            self.market_status_badge.set_status('MARKET_CLOSED')

        self.statusBar().showMessage(message, 5000)

    def _populate_sample_watchlist(self):
        """Populate watchlist with sample data."""
        sample_data = [
            {'Symbol': 'AAPL', 'Price': 185.22, 'Change': 2.34, 'Change %': 1.28, 'Volume': 52_000_000},
            {'Symbol': 'MSFT', 'Price': 420.15, 'Change': -1.50, 'Change %': -0.36, 'Volume': 28_000_000},
            {'Symbol': 'GOOGL', 'Price': 142.89, 'Change': 0.75, 'Change %': 0.53, 'Volume': 31_000_000},
            {'Symbol': 'TSLA', 'Price': 285.50, 'Change': -5.20, 'Change %': -1.79, 'Volume': 95_000_000},
            {'Symbol': 'NVDA', 'Price': 495.30, 'Change': 8.45, 'Change %': 1.74, 'Volume': 42_000_000},
        ]

        for data in sample_data:
            self.watchlist_grid.add_row(data)

    # Event handlers
    def _on_new_order(self):
        """Handle new order action."""
        dialog = OrderEntryDialog(parent=self)
        dialog.order_submitted.connect(self._submit_order)
        dialog.exec()

    def _submit_order(self, order_params: dict):
        """Submit an order from the dialog."""
        try:
            if order_params['order_type'].value == 'market':
                order = self.trading_controller.place_market_order(
                    symbol=order_params['symbol'],
                    side=order_params['side'],
                    quantity=order_params['quantity']
                )
            else:  # limit
                order = self.trading_controller.place_limit_order(
                    symbol=order_params['symbol'],
                    side=order_params['side'],
                    quantity=order_params['quantity'],
                    limit_price=order_params['limit_price']
                )

            if order:
                self.logger.info(f"Order submitted successfully: {order.client_order_id}")
        except Exception as e:
            self.logger.error(f"Error submitting order: {e}")
            QMessageBox.critical(self, "Order Error", f"Failed to submit order: {str(e)}")

    def _on_refresh_data(self):
        """Handle refresh data action."""
        self.statusBar().showMessage("Refreshing data...", 2000)
        watchlist = self.data_controller.watchlist
        if watchlist:
            self.data_controller.fetch_symbols(watchlist)
        self.logger.info("Data refresh requested")

    def _set_trading_mode(self, mode: TradingMode):
        """Set trading mode."""
        self.trading_mode = mode
        self.trading_mode_label.setText(f"Mode: {mode.value.upper()}")

        # Update label color
        color = COLORS['negative'] if mode == TradingMode.LIVE else COLORS['warning']
        self.trading_mode_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-weight: bold;
                padding: 4px 12px;
            }}
        """)

        self.logger.info(f"Trading mode set to: {mode.value}")

    def _toggle_fullscreen(self, checked: bool):
        """Toggle fullscreen mode."""
        if checked:
            self.showFullScreen()
        else:
            self.showNormal()

    def _show_about_dialog(self):
        """Show about dialog."""
        about_text = """
        <h2>AlphaFlow Trading Platform</h2>
        <p>Version 6.0.0</p>
        <p>Professional algorithmic trading platform for macOS</p>
        <br>
        <p>Built with PyQt6 and Python</p>
        <p>© 2024 AlphaFlow</p>
        """
        QMessageBox.about(self, "About AlphaFlow", about_text)

    # UI update methods
    def _update_dashboard_from_cache(self):
        """Update dashboard watchlist from cached data."""
        self.watchlist_grid.clear_data()

        for symbol in self.data_controller.watchlist:
            data = self.data_controller.get_cached_data(symbol)
            if data and 'quote' in data:
                self._update_watchlist_row(symbol, data)

    def _update_watchlist_row(self, symbol: str, data: dict):
        """Update a single watchlist row."""
        quote = data.get('quote', {})

        row_data = {
            'Symbol': symbol,
            'Price': quote.get('price', 0.0),
            'Change': quote.get('change', 0.0),
            'Change %': quote.get('change_percent', 0.0),
            'Volume': quote.get('volume', 0)
        }

        # Check if row exists, update or add
        existing_rows = self.watchlist_grid.rowCount()
        row_found = False

        for row in range(existing_rows):
            item = self.watchlist_grid.item(row, 0)
            if item and item.text() == symbol:
                self.watchlist_grid.update_row(row, row_data)
                row_found = True
                break

        if not row_found:
            self.watchlist_grid.add_row(row_data)

    def _update_dashboard_metrics(self):
        """Update dashboard metric cards."""
        portfolio_value = self.trading_controller.get_portfolio_value()
        cash = self.trading_controller.get_cash_balance()

        self.portfolio_value_card.set_value(f"${portfolio_value:,.2f}")

        # TODO: Calculate actual day P&L and other metrics
        # For now, showing cash
        self.day_pnl_card.set_value(f"${0.0:,.2f}", 0.0)

    def _update_positions_tab(self):
        """Update positions tab with current positions."""
        self.positions_grid.clear_data()

        positions = self.trading_controller.get_positions()
        for pos in positions:
            self.positions_grid.add_row(pos)

    def _update_orders_tab(self):
        """Update orders tab with order history."""
        self.orders_grid.clear_data()

        orders = self.trading_controller.get_orders()
        for order in orders:
            order_data = {
                'Time': order.created_at.strftime('%H:%M:%S') if order.created_at else '',
                'Symbol': order.symbol,
                'Side': order.side.value.upper(),
                'Quantity': order.quantity,
                'Price': order.limit_price or order.filled_avg_price or 0.0,
                'Status': order.status.value.upper()
            }
            self.orders_grid.add_row(order_data)

    # Window events
    def _on_trading_symbol_changed(self, symbol: str):
        """Handle symbol changed in trading page."""
        self.logger.info(f"Trading page symbol changed to: {symbol}")

    def _on_trading_order_requested(self, order_params: dict):
        """Handle order request from trading page."""
        try:
            # Place order via trading controller
            if order_params['order_type'] == 'MARKET':
                order = self.trading_controller.place_market_order(
                    order_params['symbol'],
                    order_params['side'],
                    order_params['quantity']
                )
            else:  # LIMIT
                order = self.trading_controller.place_limit_order(
                    order_params['symbol'],
                    order_params['side'],
                    order_params['quantity'],
                    order_params['limit_price']
                )

            if order:
                self.statusBar().showMessage(
                    f"Order placed: {order.side.value} {order.quantity} {order.symbol}",
                    3000
                )
        except Exception as e:
            self.logger.error(f"Error placing order: {e}")
            QMessageBox.critical(self, "Order Error", str(e))

    def _on_trading_data_refresh(self, symbol: str):
        """Handle data refresh request from trading page."""
        self.data_controller.fetch_symbol(symbol)

    def _on_settings_changed(self, settings: dict):
        """Handle settings changed."""
        self.logger.info("Settings changed")

        # Update trading mode if changed
        mode_str = settings.get('trading_mode', 'PAPER')
        new_mode = TradingMode[mode_str]
        if new_mode != self.trading_mode:
            self._set_trading_mode(new_mode)

        # Update data controller settings
        if settings.get('enable_streaming'):
            self.data_controller.enable_realtime_streaming(True)
        else:
            self.data_controller.enable_realtime_streaming(False)

        # Update refresh interval
        refresh_interval = settings.get('refresh_interval', 60) * 1000  # Convert to ms
        self.data_controller.stop_auto_refresh()
        self.data_controller.start_auto_refresh(refresh_interval)

    def _on_test_connection(self):
        """Handle test connection request."""
        # Simple test - try to fetch data for a known symbol
        try:
            data = self.data_controller.fetch_symbol('AAPL')
            if data:
                QMessageBox.information(
                    self,
                    "Connection Test",
                    "✓ Successfully connected to data source!\n\nData fetched for AAPL."
                )
            else:
                QMessageBox.warning(
                    self,
                    "Connection Test",
                    "⚠️ Could not fetch data.\n\nPlease check your API credentials."
                )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Connection Test",
                f"✗ Connection failed!\n\nError: {str(e)}"
            )

    def _on_strategy_started(self, strategy_id: str):
        """Handle strategy started."""
        self.logger.info(f"Strategy {strategy_id} started")
        self.statusBar().showMessage(f"Strategy {strategy_id} started", 3000)

    def _on_strategy_stopped(self, strategy_id: str):
        """Handle strategy stopped."""
        self.logger.info(f"Strategy {strategy_id} stopped")
        self.statusBar().showMessage(f"Strategy {strategy_id} stopped", 3000)

    def _on_backtest_started(self, params: dict):
        """Handle backtest started."""
        symbols = params.get('symbols', [])
        self.logger.info(f"Backtest started for {len(symbols)} symbols")
        self.statusBar().showMessage("Running backtest...", 5000)

    def _on_alert_triggered(self, alert: Alert):
        """Handle alert triggered."""
        self.logger.info(f"Alert triggered: {alert.symbol} {alert.alert_type.value}")

        # Show notification
        message = alert.message if alert.message else f"{alert.symbol}: {alert.alert_type.value}"

        # Show in status bar
        self.statusBar().showMessage(f"🔔 Alert: {message}", 10000)

        # Show message box for important alerts
        if alert.alert_type in [AlertType.PRICE_ABOVE, AlertType.PRICE_BELOW]:
            QMessageBox.information(
                self,
                "Price Alert",
                f"Alert triggered for {alert.symbol}!\n\n{message}"
            )

    def closeEvent(self, event):
        """Handle window close event."""
        # Save window geometry
        self.settings.setValue('geometry', self.saveGeometry())

        # Cleanup controllers
        self.data_controller.cleanup()
        self.trading_controller.cleanup()

        self.logger.info("AlphaFlow shutting down")
        event.accept()


def main():
    """Main entry point for AlphaFlow."""
    from PyQt6.QtWidgets import QApplication

    # Setup logging
    setup_logging()

    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("AlphaFlow")
    app.setOrganizationName("AlphaFlow")

    # Create and show main window
    window = AlphaFlowMainWindow()
    window.show()

    # Run application
    sys.exit(app.exec())

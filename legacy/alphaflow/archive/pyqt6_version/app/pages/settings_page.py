"""Settings page for API configuration and preferences."""

import logging
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QLabel, QLineEdit, QPushButton, QComboBox,
    QFormLayout, QCheckBox, QSpinBox, QMessageBox,
    QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal

from app.styles.colors import COLORS
from core import TradingMode


class SettingsPage(QWidget):
    """
    Settings page for configuring API keys, trading parameters, and preferences.

    Features:
    - API key configuration (Alpaca, News API)
    - Trading mode selection (LIVE/PAPER/ANALYSIS)
    - Risk parameters
    - UI preferences
    - Real-time streaming toggle
    """

    settings_changed = pyqtSignal(dict)  # settings dictionary
    test_connection_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)

        # Current settings (loaded from environment)
        self.current_settings = self._load_settings()

        self._init_ui()

    def _init_ui(self):
        """Initialize the user interface."""
        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)

        # Content widget
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(24)

        # Title
        title = QLabel("Settings")
        title.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text_primary']};
                font-size: 24px;
                font-weight: 700;
            }}
        """)
        layout.addWidget(title)

        # API Configuration
        api_group = self._create_api_config_group()
        layout.addWidget(api_group)

        # Trading Configuration
        trading_group = self._create_trading_config_group()
        layout.addWidget(trading_group)

        # Risk Parameters
        risk_group = self._create_risk_parameters_group()
        layout.addWidget(risk_group)

        # UI Preferences
        ui_group = self._create_ui_preferences_group()
        layout.addWidget(ui_group)

        # Save/Reset buttons
        buttons_layout = self._create_action_buttons()
        layout.addLayout(buttons_layout)

        layout.addStretch()

        scroll.setWidget(content)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

    def _create_api_config_group(self) -> QGroupBox:
        """Create API configuration group."""
        group = QGroupBox("API Configuration")
        group.setStyleSheet(f"""
            QGroupBox {{
                color: {COLORS['text_primary']};
                font-weight: 600;
                font-size: 16px;
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 16px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
            }}
        """)

        layout = QFormLayout(group)
        layout.setSpacing(16)

        # Alpaca API Key
        self.alpaca_key_input = QLineEdit()
        self.alpaca_key_input.setPlaceholderText("Enter your Alpaca API key")
        self.alpaca_key_input.setText(self.current_settings.get('alpaca_api_key', ''))
        self.alpaca_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self._style_input(self.alpaca_key_input)
        layout.addRow("Alpaca API Key:", self.alpaca_key_input)

        # Alpaca Secret Key
        self.alpaca_secret_input = QLineEdit()
        self.alpaca_secret_input.setPlaceholderText("Enter your Alpaca secret key")
        self.alpaca_secret_input.setText(self.current_settings.get('alpaca_secret_key', ''))
        self.alpaca_secret_input.setEchoMode(QLineEdit.EchoMode.Password)
        self._style_input(self.alpaca_secret_input)
        layout.addRow("Alpaca Secret Key:", self.alpaca_secret_input)

        # Test connection button
        test_btn = QPushButton("Test Connection")
        test_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['accent_alt']};
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
        test_btn.clicked.connect(self.test_connection_requested.emit)
        layout.addRow("", test_btn)

        # News API Key (optional)
        self.news_api_input = QLineEdit()
        self.news_api_input.setPlaceholderText("Enter your News API key (optional)")
        self.news_api_input.setText(self.current_settings.get('news_api_key', ''))
        self.news_api_input.setEchoMode(QLineEdit.EchoMode.Password)
        self._style_input(self.news_api_input)
        layout.addRow("News API Key:", self.news_api_input)

        return group

    def _create_trading_config_group(self) -> QGroupBox:
        """Create trading configuration group."""
        group = QGroupBox("Trading Configuration")
        group.setStyleSheet(f"""
            QGroupBox {{
                color: {COLORS['text_primary']};
                font-weight: 600;
                font-size: 16px;
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 16px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
            }}
        """)

        layout = QFormLayout(group)
        layout.setSpacing(16)

        # Trading Mode
        self.trading_mode_combo = QComboBox()
        self.trading_mode_combo.addItems(["PAPER", "LIVE", "BACKTEST", "ANALYSIS"])
        current_mode = self.current_settings.get('trading_mode', 'PAPER')
        self.trading_mode_combo.setCurrentText(current_mode)
        self._style_combo(self.trading_mode_combo)
        layout.addRow("Trading Mode:", self.trading_mode_combo)

        # Warning label for LIVE mode
        self.live_warning = QLabel("⚠️ LIVE mode uses real money! Test thoroughly in PAPER mode first.")
        self.live_warning.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['negative']};
                font-weight: 600;
                padding: 8px;
                background-color: rgba(255, 82, 71, 0.1);
                border-radius: 4px;
            }}
        """)
        self.live_warning.setWordWrap(True)
        self.live_warning.setVisible(current_mode == "LIVE")
        layout.addRow("", self.live_warning)

        self.trading_mode_combo.currentTextChanged.connect(
            lambda mode: self.live_warning.setVisible(mode == "LIVE")
        )

        # Enable real-time streaming
        self.streaming_checkbox = QCheckBox("Enable Real-Time WebSocket Streaming")
        self.streaming_checkbox.setChecked(self.current_settings.get('enable_streaming', False))
        self.streaming_checkbox.setStyleSheet(f"""
            QCheckBox {{
                color: {COLORS['text_primary']};
            }}
            QCheckBox::indicator {{
                width: 20px;
                height: 20px;
            }}
        """)
        layout.addRow("", self.streaming_checkbox)

        return group

    def _create_risk_parameters_group(self) -> QGroupBox:
        """Create risk parameters group."""
        group = QGroupBox("Risk Parameters")
        group.setStyleSheet(f"""
            QGroupBox {{
                color: {COLORS['text_primary']};
                font-weight: 600;
                font-size: 16px;
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 16px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
            }}
        """)

        layout = QFormLayout(group)
        layout.setSpacing(16)

        # Max position size (%)
        self.max_position_spin = QSpinBox()
        self.max_position_spin.setMinimum(1)
        self.max_position_spin.setMaximum(100)
        self.max_position_spin.setValue(self.current_settings.get('max_position_size', 10))
        self.max_position_spin.setSuffix(" %")
        self._style_spinbox(self.max_position_spin)
        layout.addRow("Max Position Size:", self.max_position_spin)

        # Max daily loss (%)
        self.max_daily_loss_spin = QSpinBox()
        self.max_daily_loss_spin.setMinimum(1)
        self.max_daily_loss_spin.setMaximum(100)
        self.max_daily_loss_spin.setValue(self.current_settings.get('max_daily_loss', 2))
        self.max_daily_loss_spin.setSuffix(" %")
        self._style_spinbox(self.max_daily_loss_spin)
        layout.addRow("Max Daily Loss:", self.max_daily_loss_spin)

        # Stop loss default (%)
        self.stop_loss_spin = QSpinBox()
        self.stop_loss_spin.setMinimum(1)
        self.stop_loss_spin.setMaximum(50)
        self.stop_loss_spin.setValue(self.current_settings.get('default_stop_loss', 5))
        self.stop_loss_spin.setSuffix(" %")
        self._style_spinbox(self.stop_loss_spin)
        layout.addRow("Default Stop Loss:", self.stop_loss_spin)

        # Take profit default (%)
        self.take_profit_spin = QSpinBox()
        self.take_profit_spin.setMinimum(1)
        self.take_profit_spin.setMaximum(100)
        self.take_profit_spin.setValue(self.current_settings.get('default_take_profit', 10))
        self.take_profit_spin.setSuffix(" %")
        self._style_spinbox(self.take_profit_spin)
        layout.addRow("Default Take Profit:", self.take_profit_spin)

        return group

    def _create_ui_preferences_group(self) -> QGroupBox:
        """Create UI preferences group."""
        group = QGroupBox("UI Preferences")
        group.setStyleSheet(f"""
            QGroupBox {{
                color: {COLORS['text_primary']};
                font-weight: 600;
                font-size: 16px;
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 16px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
            }}
        """)

        layout = QFormLayout(group)
        layout.setSpacing(16)

        # Auto-refresh interval (seconds)
        self.refresh_interval_spin = QSpinBox()
        self.refresh_interval_spin.setMinimum(5)
        self.refresh_interval_spin.setMaximum(300)
        self.refresh_interval_spin.setValue(self.current_settings.get('refresh_interval', 60))
        self.refresh_interval_spin.setSuffix(" seconds")
        self._style_spinbox(self.refresh_interval_spin)
        layout.addRow("Data Refresh Interval:", self.refresh_interval_spin)

        # Show notifications
        self.notifications_checkbox = QCheckBox("Show Trade Notifications")
        self.notifications_checkbox.setChecked(self.current_settings.get('show_notifications', True))
        self.notifications_checkbox.setStyleSheet(f"""
            QCheckBox {{
                color: {COLORS['text_primary']};
            }}
            QCheckBox::indicator {{
                width: 20px;
                height: 20px;
            }}
        """)
        layout.addRow("", self.notifications_checkbox)

        return group

    def _create_action_buttons(self) -> QHBoxLayout:
        """Create action buttons layout."""
        layout = QHBoxLayout()
        layout.addStretch()

        # Reset button
        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['bg_elevated']};
                color: {COLORS['text_secondary']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                border-color: {COLORS['accent_alt']};
                color: {COLORS['text_primary']};
            }}
        """)
        reset_btn.clicked.connect(self._on_reset)
        layout.addWidget(reset_btn)

        # Save button
        save_btn = QPushButton("Save Settings")
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['positive']};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 24px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: #00D67E;
            }}
        """)
        save_btn.clicked.connect(self._on_save)
        layout.addWidget(save_btn)

        return layout

    def _style_input(self, widget: QLineEdit):
        """Apply consistent styling to input widgets."""
        widget.setStyleSheet(f"""
            QLineEdit {{
                background-color: {COLORS['bg_elevated']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
            }}
            QLineEdit:focus {{
                border-color: {COLORS['accent_alt']};
            }}
        """)

    def _style_combo(self, widget: QComboBox):
        """Apply consistent styling to combo box widgets."""
        widget.setStyleSheet(f"""
            QComboBox {{
                background-color: {COLORS['bg_elevated']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
            }}
            QComboBox:focus {{
                border-color: {COLORS['accent_alt']};
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

    def _style_spinbox(self, widget: QSpinBox):
        """Apply consistent styling to spinbox widgets."""
        widget.setStyleSheet(f"""
            QSpinBox {{
                background-color: {COLORS['bg_elevated']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
            }}
            QSpinBox:focus {{
                border-color: {COLORS['accent_alt']};
            }}
        """)

    def _load_settings(self) -> dict:
        """Load current settings from environment and defaults."""
        return {
            'alpaca_api_key': os.getenv('ALPACA_API_KEY', ''),
            'alpaca_secret_key': os.getenv('ALPACA_SECRET_KEY', ''),
            'news_api_key': os.getenv('NEWS_API_KEY', ''),
            'trading_mode': 'PAPER',
            'enable_streaming': False,
            'max_position_size': 10,
            'max_daily_loss': 2,
            'default_stop_loss': 5,
            'default_take_profit': 10,
            'refresh_interval': 60,
            'show_notifications': True,
        }

    def _on_save(self):
        """Handle save button click."""
        # Collect settings
        settings = {
            'alpaca_api_key': self.alpaca_key_input.text(),
            'alpaca_secret_key': self.alpaca_secret_input.text(),
            'news_api_key': self.news_api_input.text(),
            'trading_mode': self.trading_mode_combo.currentText(),
            'enable_streaming': self.streaming_checkbox.isChecked(),
            'max_position_size': self.max_position_spin.value(),
            'max_daily_loss': self.max_daily_loss_spin.value(),
            'default_stop_loss': self.stop_loss_spin.value(),
            'default_take_profit': self.take_profit_spin.value(),
            'refresh_interval': self.refresh_interval_spin.value(),
            'show_notifications': self.notifications_checkbox.isChecked(),
        }

        # Save to .env file
        self._save_to_env_file(settings)

        # Emit signal
        self.settings_changed.emit(settings)

        # Show confirmation
        QMessageBox.information(
            self,
            "Settings Saved",
            "Settings have been saved successfully. Some changes may require restarting the application."
        )

    def _on_reset(self):
        """Handle reset button click."""
        reply = QMessageBox.question(
            self,
            "Reset Settings",
            "Are you sure you want to reset all settings to defaults?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            defaults = self._load_settings()
            self._apply_settings(defaults)

    def _apply_settings(self, settings: dict):
        """Apply settings to UI widgets."""
        self.alpaca_key_input.setText(settings.get('alpaca_api_key', ''))
        self.alpaca_secret_input.setText(settings.get('alpaca_secret_key', ''))
        self.news_api_input.setText(settings.get('news_api_key', ''))
        self.trading_mode_combo.setCurrentText(settings.get('trading_mode', 'PAPER'))
        self.streaming_checkbox.setChecked(settings.get('enable_streaming', False))
        self.max_position_spin.setValue(settings.get('max_position_size', 10))
        self.max_daily_loss_spin.setValue(settings.get('max_daily_loss', 2))
        self.stop_loss_spin.setValue(settings.get('default_stop_loss', 5))
        self.take_profit_spin.setValue(settings.get('default_take_profit', 10))
        self.refresh_interval_spin.setValue(settings.get('refresh_interval', 60))
        self.notifications_checkbox.setChecked(settings.get('show_notifications', True))

    def _save_to_env_file(self, settings: dict):
        """Save settings to .env file."""
        env_path = os.path.join(os.getcwd(), '.env')

        # Read existing .env content
        existing_lines = []
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                existing_lines = f.readlines()

        # Update or add settings
        env_vars = {
            'ALPACA_API_KEY': settings['alpaca_api_key'],
            'ALPACA_SECRET_KEY': settings['alpaca_secret_key'],
            'NEWS_API_KEY': settings['news_api_key'],
        }

        new_lines = []
        updated_keys = set()

        for line in existing_lines:
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                key = line.split('=')[0]
                if key in env_vars:
                    new_lines.append(f"{key}={env_vars[key]}\n")
                    updated_keys.add(key)
                else:
                    new_lines.append(line + '\n')
            else:
                new_lines.append(line + '\n')

        # Add new keys
        for key, value in env_vars.items():
            if key not in updated_keys:
                new_lines.append(f"{key}={value}\n")

        # Write back to file
        with open(env_path, 'w') as f:
            f.writelines(new_lines)

        self.logger.info("Settings saved to .env file")

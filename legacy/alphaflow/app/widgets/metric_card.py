"""Metric card widget for displaying key metrics on the dashboard."""

from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, pyqtProperty, QPropertyAnimation
from PyQt6.QtGui import QFont, QColor
from typing import Optional

from app.styles import COLORS


class MetricCard(QFrame):
    """
    A card widget for displaying a single metric with label, value, and change indicator.

    Used on dashboards to show key portfolio metrics like:
    - Portfolio Value
    - Day P&L
    - Total Return
    - Win Rate
    etc.
    """

    def __init__(
        self,
        label: str,
        value: str = "$0.00",
        change: Optional[float] = None,
        parent=None
    ):
        super().__init__(parent)
        self.label_text = label
        self.value_text = value
        self.change_value = change

        self._setup_ui()
        self._apply_styling()

    def _setup_ui(self):
        """Setup the UI components."""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(8)

        # Label (metric name)
        self.label_widget = QLabel(self.label_text)
        self.label_widget.setObjectName("MetricLabel")
        self.label_widget.setWordWrap(False)
        label_font = QFont()
        label_font.setFamilies(['-apple-system', 'SF Pro Display', 'Segoe UI'])
        label_font.setPointSize(11)
        label_font.setWeight(QFont.Weight.DemiBold)
        self.label_widget.setFont(label_font)
        self.label_widget.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text_secondary']};
                text-transform: uppercase;
                letter-spacing: 1px;
                padding: 0px;
            }}
        """)

        # Value (main metric)
        self.value_widget = QLabel(self.value_text)
        self.value_widget.setObjectName("MetricValue")
        self.value_widget.setWordWrap(False)
        self.value_widget.setMinimumHeight(50)
        value_font = QFont()
        value_font.setFamilies(['SF Mono', 'Menlo', 'Monaco', 'Consolas', 'monospace'])
        value_font.setPointSize(28)
        value_font.setWeight(QFont.Weight.Bold)
        self.value_widget.setFont(value_font)
        self.value_widget.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text_primary']};
                padding: 4px 0px;
            }}
        """)

        # Change indicator (optional)
        self.change_widget = QLabel()
        change_font = QFont()
        change_font.setFamilies(['Menlo', 'Monaco', 'Consolas'])
        change_font.setPointSize(12)
        self.change_widget.setFont(change_font)

        if self.change_value is not None:
            self._update_change_display(self.change_value)

        layout.addWidget(self.label_widget)
        layout.addWidget(self.value_widget)
        if self.change_value is not None:
            layout.addWidget(self.change_widget)

        layout.addStretch()

        self.setLayout(layout)

    def _apply_styling(self):
        """Apply card styling."""
        self.setObjectName("CardFrame")
        self.setStyleSheet(f"""
            QFrame#CardFrame {{
                background-color: {COLORS['bg_secondary']};
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
                padding: 8px;
            }}
            QFrame#CardFrame:hover {{
                background-color: {COLORS['bg_hover']};
                border-color: {COLORS['border_light']};
            }}
        """)
        self.setMinimumSize(200, 140)
        self.setMaximumHeight(180)

    def _update_change_display(self, change: float):
        """Update the change indicator display."""
        # Format change
        prefix = "+" if change >= 0 else ""
        change_text = f"{prefix}{change:.2f}%"

        # Set arrow
        arrow = "↑" if change >= 0 else "↓"
        full_text = f"{arrow} {change_text}"

        self.change_widget.setText(full_text)

        # Set color
        if change > 0:
            color = COLORS['positive']
        elif change < 0:
            color = COLORS['negative']
        else:
            color = COLORS['text_secondary']

        self.change_widget.setStyleSheet(f"""
            QLabel {{
                color: {color};
            }}
        """)

    def set_value(self, value: str, change: Optional[float] = None, animate: bool = False):
        """
        Update the metric value.

        Args:
            value: New value string (e.g., "$123,456.78")
            change: Optional change percentage
            animate: Whether to animate the value change
        """
        self.value_text = value
        self.value_widget.setText(value)

        if change is not None:
            self.change_value = change
            self._update_change_display(change)

            # Show change widget if it was hidden
            if not self.change_widget.isVisible():
                self.change_widget.setVisible(True)

        # TODO: Add animation for value changes
        if animate:
            self._animate_value_change()

    def _animate_value_change(self):
        """Animate value change (placeholder for future enhancement)."""
        # Could implement:
        # - Number counter animation
        # - Color pulse
        # - Scale animation
        pass

    def set_label(self, label: str):
        """
        Update the metric label.

        Args:
            label: New label text
        """
        self.label_text = label
        self.label_widget.setText(label)

    def get_value(self) -> str:
        """Get current value."""
        return self.value_text

    def get_change(self) -> Optional[float]:
        """Get current change percentage."""
        return self.change_value


class CompactMetricCard(QFrame):
    """
    A more compact version of MetricCard for dense layouts.

    Displays label and value side-by-side instead of stacked.
    """

    def __init__(self, label: str, value: str = "$0.00", parent=None):
        super().__init__(parent)
        self.label_text = label
        self.value_text = value

        self._setup_ui()
        self._apply_styling()

    def _setup_ui(self):
        """Setup the UI components."""
        from PyQt6.QtWidgets import QHBoxLayout

        layout = QHBoxLayout()
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(8)

        # Label
        self.label_widget = QLabel(self.label_text)
        label_font = QFont()
        label_font.setFamilies(['Inter', 'SF Pro Display', 'Segoe UI'])
        label_font.setPointSize(11)
        self.label_widget.setFont(label_font)
        self.label_widget.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text_secondary']};
            }}
        """)

        # Value
        self.value_widget = QLabel(self.value_text)
        value_font = QFont()
        value_font.setFamilies(['Menlo', 'Monaco', 'Consolas'])
        value_font.setPointSize(13)
        value_font.setWeight(QFont.Weight.Bold)
        self.value_widget.setFont(value_font)
        self.value_widget.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text_primary']};
            }}
        """)

        layout.addWidget(self.label_widget)
        layout.addStretch()
        layout.addWidget(self.value_widget)

        self.setLayout(layout)

    def _apply_styling(self):
        """Apply card styling."""
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_secondary']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
            }}
        """)
        self.setFixedHeight(50)

    def set_value(self, value: str):
        """Update the value."""
        self.value_text = value
        self.value_widget.setText(value)

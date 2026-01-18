"""Bloomberg-style data grid widget for AlphaFlow."""

from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QColor, QBrush, QFont
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.styles import COLORS


class BloombergDataGrid(QTableWidget):
    """
    Professional financial data grid inspired by Bloomberg Terminal.

    Features:
    - Right-aligned numeric columns
    - Monospace font for numbers
    - Alternating row colors
    - Real-time cell updates with color flash animation
    - Sortable columns
    - Professional styling
    """

    cell_clicked = pyqtSignal(int, int)  # row, column
    row_double_clicked = pyqtSignal(int)  # row

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_grid()
        self._setup_fonts()
        self._previous_values = {}  # Track previous values for flash animation

    def _setup_grid(self):
        """Setup grid appearance and behavior."""
        # Visual settings
        self.setAlternatingRowColors(True)
        self.setShowGrid(True)
        self.setGridStyle(Qt.PenStyle.SolidLine)

        # Selection settings
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

        # Header settings
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setSectionsMovable(False)
        self.verticalHeader().setVisible(False)

        # Enable sorting
        self.setSortingEnabled(True)

        # Connect signals
        self.cellClicked.connect(self._on_cell_clicked)
        self.cellDoubleClicked.connect(self._on_cell_double_clicked)

    def _setup_fonts(self):
        """Setup fonts for different column types."""
        # Regular font for text columns
        self.text_font = QFont()
        self.text_font.setFamilies(['Inter', 'SF Pro Display', 'Segoe UI', 'Arial'])
        self.text_font.setPointSize(12)

        # Monospace font for numeric columns
        self.mono_font = QFont()
        self.mono_font.setFamilies(['Menlo', 'Monaco', 'Consolas', 'Courier New'])
        self.mono_font.setPointSize(12)

    def set_columns(self, headers: List[str], numeric_columns: Optional[List[str]] = None):
        """
        Set column headers.

        Args:
            headers: List of column header names
            numeric_columns: List of column names that should be right-aligned with monospace font
        """
        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)
        self.numeric_columns = set(numeric_columns or [])

        # Store column indices
        self.column_map = {header: idx for idx, header in enumerate(headers)}

        # Resize columns to content
        self.resizeColumnsToContents()

    def add_row(self, data: Dict[str, Any]):
        """
        Add a row to the grid.

        Args:
            data: Dictionary mapping column names to values
        """
        row_position = self.rowCount()
        self.insertRow(row_position)

        for column_name, value in data.items():
            if column_name in self.column_map:
                col_idx = self.column_map[column_name]
                self._set_cell_value(row_position, col_idx, value, column_name)

    def update_row(self, row: int, data: Dict[str, Any]):
        """
        Update an existing row.

        Args:
            row: Row index
            data: Dictionary mapping column names to values
        """
        if row >= self.rowCount():
            return

        for column_name, value in data.items():
            if column_name in self.column_map:
                col_idx = self.column_map[column_name]
                self._set_cell_value(row, col_idx, value, column_name, animate=True)

    def _set_cell_value(self, row: int, col: int, value: Any, column_name: str, animate: bool = False):
        """
        Set cell value with appropriate formatting.

        Args:
            row: Row index
            col: Column index
            value: Cell value
            column_name: Column name for formatting
            animate: Whether to animate value changes
        """
        item = QTableWidgetItem()

        # Format value
        if isinstance(value, float):
            if 'percent' in column_name.lower() or 'change' in column_name.lower():
                # Percentage formatting
                formatted = f"{value:+.2f}%"
                # Color code positive/negative
                if value > 0:
                    item.setForeground(QBrush(QColor(COLORS['positive'])))
                elif value < 0:
                    item.setForeground(QBrush(QColor(COLORS['negative'])))
            elif 'price' in column_name.lower() or 'value' in column_name.lower():
                # Currency formatting
                formatted = f"${value:,.2f}"
            else:
                # General float formatting
                formatted = f"{value:,.4f}".rstrip('0').rstrip('.')
        elif isinstance(value, int):
            if 'volume' in column_name.lower():
                # Volume formatting (abbreviated)
                if value >= 1_000_000:
                    formatted = f"{value / 1_000_000:.2f}M"
                elif value >= 1_000:
                    formatted = f"{value / 1_000:.2f}K"
                else:
                    formatted = f"{value:,}"
            else:
                formatted = f"{value:,}"
        elif isinstance(value, datetime):
            formatted = value.strftime('%Y-%m-%d %H:%M:%S')
        else:
            formatted = str(value)

        item.setText(formatted)

        # Set font
        if column_name in self.numeric_columns:
            item.setFont(self.mono_font)
            item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        else:
            item.setFont(self.text_font)
            item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        # Store for sorting
        if isinstance(value, (int, float)):
            item.setData(Qt.ItemDataRole.UserRole, value)

        self.setItem(row, col, item)

        # Animate value change if requested
        if animate:
            cell_key = (row, col)
            previous_value = self._previous_values.get(cell_key)

            if previous_value is not None and previous_value != value:
                if isinstance(value, (int, float)) and isinstance(previous_value, (int, float)):
                    # Flash green if increased, red if decreased
                    flash_color = COLORS['positive'] if value > previous_value else COLORS['negative']
                    self._flash_cell(row, col, flash_color)

            self._previous_values[cell_key] = value

    def _flash_cell(self, row: int, col: int, color: str):
        """
        Flash a cell with a color to indicate change.

        Args:
            row: Row index
            col: Column index
            color: Hex color code
        """
        item = self.item(row, col)
        if not item:
            return

        # Store original color
        original_brush = item.foreground()

        # Set flash color
        item.setForeground(QBrush(QColor(color)))

        # TODO: Implement QPropertyAnimation for smooth color fade
        # For now, we'll use a simple timer-based approach
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(300, lambda: item.setForeground(original_brush))

    def clear_data(self):
        """Clear all rows but keep headers."""
        self.setRowCount(0)
        self._previous_values.clear()

    def get_selected_row_data(self) -> Optional[Dict[str, Any]]:
        """
        Get data from the currently selected row.

        Returns:
            Dictionary mapping column names to values, or None if no selection
        """
        selected_rows = self.selectionModel().selectedRows()
        if not selected_rows:
            return None

        row = selected_rows[0].row()
        data = {}

        for column_name, col_idx in self.column_map.items():
            item = self.item(row, col_idx)
            if item:
                # Try to get numeric value from UserRole
                value = item.data(Qt.ItemDataRole.UserRole)
                if value is None:
                    value = item.text()
                data[column_name] = value

        return data

    def _on_cell_clicked(self, row: int, column: int):
        """Handle cell click event."""
        self.cell_clicked.emit(row, column)

    def _on_cell_double_clicked(self, row: int, column: int):
        """Handle cell double-click event."""
        self.row_double_clicked.emit(row)

    def set_row_count(self, count: int):
        """Set number of rows."""
        self.setRowCount(count)

    def sort_by_column(self, column: str, descending: bool = False):
        """
        Sort table by column name.

        Args:
            column: Column name
            descending: Sort in descending order
        """
        if column in self.column_map:
            col_idx = self.column_map[column]
            order = Qt.SortOrder.DescendingOrder if descending else Qt.SortOrder.AscendingOrder
            self.sortItems(col_idx, order)

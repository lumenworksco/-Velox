"""Bloomberg Terminal-inspired Qt stylesheet for AlphaFlow."""

from .colors import COLORS

# ============================================================================
# BLOOMBERG TERMINAL QSS STYLESHEET
# ============================================================================

BLOOMBERG_STYLESHEET = f"""
/* ========== Global Widget Styling ========== */
QWidget {{
    background-color: {COLORS['bg_primary']};
    color: {COLORS['text_primary']};
    font-family: 'Inter', 'SF Pro Display', 'Segoe UI', Arial, sans-serif;
    font-size: 13px;
}}

/* ========== Frames/Panels ========== */
QFrame {{
    background-color: {COLORS['bg_secondary']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    padding: 8px;
}}

QFrame#CardFrame {{
    background-color: {COLORS['bg_secondary']};
    border: 1px solid {COLORS['border']};
    border-radius: 12px;
    padding: 16px;
}}

QFrame#SidebarFrame {{
    background-color: {COLORS['bg_tertiary']};
    border: none;
    border-right: 1px solid {COLORS['border']};
    border-radius: 0px;
}}

/* ========== Labels ========== */
QLabel {{
    background: transparent;
    color: {COLORS['text_primary']};
    border: none;
}}

QLabel#MetricValue {{
    font-size: 24px;
    font-weight: bold;
    color: {COLORS['text_primary']};
}}

QLabel#MetricLabel {{
    font-size: 11px;
    color: {COLORS['text_secondary']};
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

QLabel#SectionHeader {{
    font-size: 16px;
    font-weight: 600;
    color: {COLORS['text_primary']};
}}

/* ========== Buttons ========== */
QPushButton {{
    background-color: {COLORS['bg_elevated']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 500;
}}

QPushButton:hover {{
    background-color: {COLORS['accent_alt']};
    border-color: {COLORS['accent_alt']};
    color: #FFFFFF;
}}

QPushButton:pressed {{
    background-color: {COLORS['bg_hover']};
}}

QPushButton:disabled {{
    background-color: {COLORS['bg_secondary']};
    color: {COLORS['text_tertiary']};
    border-color: {COLORS['border']};
}}

QPushButton#BuyButton {{
    background-color: {COLORS['positive']};
    color: #FFFFFF;
    border: none;
}}

QPushButton#BuyButton:hover {{
    background-color: #00E680;
}}

QPushButton#SellButton {{
    background-color: {COLORS['negative']};
    color: #FFFFFF;
    border: none;
}}

QPushButton#SellButton:hover {{
    background-color: #FF6B78;
}}

/* ========== Input Fields ========== */
QLineEdit, QTextEdit, QPlainTextEdit {{
    background-color: {COLORS['bg_elevated']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    padding: 6px 12px;
    selection-background-color: {COLORS['accent_alt']};
}}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
    border-color: {COLORS['accent_alt']};
}}

/* ========== Combo Box (Dropdown) ========== */
QComboBox {{
    background-color: {COLORS['bg_elevated']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    padding: 6px 12px;
}}

QComboBox:hover {{
    border-color: {COLORS['accent_alt']};
}}

QComboBox::drop-down {{
    border: none;
    padding-right: 8px;
}}

QComboBox::down-arrow {{
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 6px solid {COLORS['text_secondary']};
    margin-right: 4px;
}}

QComboBox QAbstractItemView {{
    background-color: {COLORS['bg_elevated']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    selection-background-color: {COLORS['accent_alt']};
    outline: none;
}}

/* ========== Spin Boxes ========== */
QSpinBox, QDoubleSpinBox {{
    background-color: {COLORS['bg_elevated']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    padding: 6px;
}}

/* ========== Tables ========== */
QTableWidget, QTableView {{
    background-color: {COLORS['bg_primary']};
    alternate-background-color: {COLORS['bg_secondary']};
    color: {COLORS['text_primary']};
    gridline-color: {COLORS['border']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    selection-background-color: {COLORS['accent_alt']};
    selection-color: #FFFFFF;
}}

QTableWidget::item, QTableView::item {{
    padding: 6px;
    border: none;
}}

QTableWidget::item:selected, QTableView::item:selected {{
    background-color: {COLORS['accent_alt']};
    color: #FFFFFF;
}}

QHeaderView::section {{
    background-color: {COLORS['bg_secondary']};
    color: {COLORS['text_secondary']};
    border: none;
    border-right: 1px solid {COLORS['border']};
    border-bottom: 1px solid {COLORS['border']};
    padding: 8px;
    font-weight: 600;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

QHeaderView::section:hover {{
    background-color: {COLORS['bg_hover']};
}}

/* ========== Scroll Bars ========== */
QScrollBar:vertical {{
    background: {COLORS['bg_secondary']};
    width: 12px;
    border: none;
    margin: 0px;
}}

QScrollBar::handle:vertical {{
    background: {COLORS['accent_alt']};
    min-height: 20px;
    border-radius: 6px;
    margin: 2px;
}}

QScrollBar::handle:vertical:hover {{
    background: {COLORS['accent_alt']};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QScrollBar:horizontal {{
    background: {COLORS['bg_secondary']};
    height: 12px;
    border: none;
    margin: 0px;
}}

QScrollBar::handle:horizontal {{
    background: {COLORS['accent_alt']};
    min-width: 20px;
    border-radius: 6px;
    margin: 2px;
}}

QScrollBar::handle:horizontal:hover {{
    background: {COLORS['accent_alt']};
}}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0px;
}}

/* ========== Tab Widget ========== */
QTabWidget::pane {{
    background-color: {COLORS['bg_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
}}

QTabBar::tab {{
    background-color: {COLORS['bg_secondary']};
    color: {COLORS['text_secondary']};
    border: 1px solid {COLORS['border']};
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    padding: 8px 16px;
    margin-right: 2px;
}}

QTabBar::tab:selected {{
    background-color: {COLORS['bg_primary']};
    color: {COLORS['text_primary']};
    font-weight: 600;
}}

QTabBar::tab:hover {{
    background-color: {COLORS['bg_hover']};
}}

/* ========== Progress Bar ========== */
QProgressBar {{
    background-color: {COLORS['bg_secondary']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    text-align: center;
    color: {COLORS['text_primary']};
}}

QProgressBar::chunk {{
    background-color: {COLORS['accent']};
    border-radius: 5px;
}}

/* ========== Tool Tip ========== */
QToolTip {{
    background-color: {COLORS['bg_elevated']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 4px;
    padding: 4px 8px;
}}

/* ========== Menu Bar ========== */
QMenuBar {{
    background-color: {COLORS['bg_secondary']};
    color: {COLORS['text_primary']};
    border-bottom: 1px solid {COLORS['border']};
    padding: 4px;
}}

QMenuBar::item {{
    background: transparent;
    padding: 6px 12px;
    border-radius: 4px;
}}

QMenuBar::item:selected {{
    background-color: {COLORS['bg_hover']};
}}

QMenu {{
    background-color: {COLORS['bg_elevated']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    padding: 4px;
}}

QMenu::item {{
    background: transparent;
    padding: 8px 24px 8px 12px;
    border-radius: 4px;
}}

QMenu::item:selected {{
    background-color: {COLORS['accent_alt']};
    color: #FFFFFF;
}}

/* ========== Status Bar ========== */
QStatusBar {{
    background-color: {COLORS['bg_secondary']};
    color: {COLORS['text_secondary']};
    border-top: 1px solid {COLORS['border']};
}}

QStatusBar::item {{
    border: none;
}}

/* ========== Group Box ========== */
QGroupBox {{
    background-color: {COLORS['bg_secondary']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 12px;
    font-weight: 600;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 12px;
    padding: 0 8px;
    color: {COLORS['text_primary']};
}}

/* ========== Checkbox & Radio Button ========== */
QCheckBox, QRadioButton {{
    color: {COLORS['text_primary']};
    spacing: 8px;
}}

QCheckBox::indicator, QRadioButton::indicator {{
    width: 18px;
    height: 18px;
    border: 2px solid {COLORS['border']};
    border-radius: 4px;
    background-color: {COLORS['bg_elevated']};
}}

QCheckBox::indicator:checked, QRadioButton::indicator:checked {{
    background-color: {COLORS['accent_alt']};
    border-color: {COLORS['accent_alt']};
}}

QRadioButton::indicator {{
    border-radius: 9px;
}}

/* ========== Splitter ========== */
QSplitter::handle {{
    background-color: {COLORS['border']};
}}

QSplitter::handle:horizontal {{
    width: 2px;
}}

QSplitter::handle:vertical {{
    height: 2px;
}}

QSplitter::handle:hover {{
    background-color: {COLORS['accent_alt']};
}}
"""

def get_stylesheet():
    """Return the Bloomberg-inspired stylesheet."""
    return BLOOMBERG_STYLESHEET
